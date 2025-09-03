#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# Modif Date v1.1 : July 2024
# version ='1.1'
# ---------------------------------------------------------------------------
"""
Script principal du programme Osmose Cracker,
chargé de récupérer les faux positifs d'Osmose/OSM
et de les transformer en signalements Espace Collaboratif IGN.

Parameters
----------
args : 'sys'
    Paramètres saisis par l'utilisateur,
    inclus dans un ensemble de paramètres énumérés 
    ci-dessous (main->parser->argument)
    et dans la documentation.

Returns
-------
osmosecracker_database: 'sql'
    Élément mis à jour avec les nouvelles données
    collectées et actualisation des statuts des
    signalements Espace Collaboratif déjà effectués.

signalement espace co: 'str'
    Autant de signalements que de nouvelles 
    données (hors ZICAD) 
    si le paramètre --type_signalement est paramétré pour.

issues_{status}_{timestamp}.csv: 'csv'
    Crée un fichier CSV des données collectées 
    si --write_csv a été paramétré pour.

log : 'str'
    Suivi de la vie du programme.

Note
----
Le programme comporte encore des parties en développement,
telles que l'appel à l'API OSM, qui n'a pas encore été implémenté.
"""
# ---------------------------------------------------------------------------

# Imports
import argparse
from dataclass_csv import DataclassWriter
from datetime import date, timedelta,datetime
import re
import datetime
import json
import logging
import math
import pathlib
import sys
import requests
from time import sleep
from typing import Final
import osmosecracker_config as config
from osmosecracker_database_management import osmosecrackerDatabase
import osmosecracker_espacecollaboratifign
import osmosecracker_exceptions
import osmosecracker_issue
import osmosecracker_query_bduni
import osmosecracker_query_osmose


# Définition du logging
# On utilise la librairie standard 'logging'
# Le logger principal s'appelle OsmoseCracker ( primare logger OSM cracker )
# les autres en sont des enfants (OsmoseCracker.***)
LOGGER = logging.getLogger("OsmoseCracker")
LOGGER.setLevel(logging.DEBUG)
loggingformatter = logging.Formatter('%(asctime)s %(process)d %(name)s %(levelname)-8s %(message)s')
# Définition du StreamHandler (console)
consolestreamhandler = logging.StreamHandler()
# Définition du fichier de log
filename_log = str(pathlib.Path(__file__).resolve().parent.parent.joinpath('Logs').joinpath('OsmoseCrackerLog_' + str(date.today()) + '.log'))
filestreamhandler = logging.FileHandler(filename=filename_log, encoding='utf-8')
filestreamhandler.setFormatter(loggingformatter)
# Attachement du/des handler
LOGGER.addHandler(consolestreamhandler)
LOGGER.addHandler(filestreamhandler)


def main(args):    
    # Main de OsmoseCracker
    # Définition des arguments du script
    parser = argparse.ArgumentParser(
        prog="Osmose cracker",
        description="""Osmose cracker, récupérer les faux positifs d'Osmose/OSM et les transformer en signalements Espace Collaboratif IGN.""",
        allow_abbrev=False)

    parser.add_argument("-ecso", "--espace_co_statuses_only",
                        type=bool,
                        default=False,
                        help="""Si besoins seulement d'actualiser les signalements espace CO""")

    parser.add_argument("-c", "--country",
                        nargs="+",
                        type=str,
                        default=["france", "france_local_db"],
                        help="""Valeur de country d'Osmose sur laquelle l'analyzer choisi a été executé.
                        Attention, les country ne sont pas explicitement emboitées (https://github.com/osm-fr/osmose-backend/issues/2045#issuecomment-1759535629)
                        La zone géographique ciblée par défaut est la France entière""")

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-fdep", "--filtredep",
                        nargs="+",
                        type=str,
                        # default=["69"],
                        help="""Tableau de string des codes INSEE des départements au sens service de l'état pour lesquels les signalements Osmose doivent être téléchargés.""")

    group.add_argument("-freg", "--filtrereg",
                        nargs="+",
                        type=str,
                        # default=["ARA"],
                        help="""Tableau de string des codes INSEE des régions pour lesquels les signalements Osmose doivent être téléchargés.""")

    parser.add_argument("-sd", "--start_date",
                        type=datetime.date.fromisoformat,
                        default=(datetime.datetime.now() - datetime.timedelta(days=31)).date().isoformat(),
                        help="""La date des premiere données demandé
                        (au format ISO, YYYY-MM-DD)""")

    parser.add_argument("-ed", "--end_date",
                        type=datetime.date.fromisoformat,
                        default=datetime.datetime.now().date().isoformat(),
                        help="""La date des dernier données demandé
                        (au format ISO, YYYY-MM-DD)""")

    parser.add_argument("-s", "--status",
                        choices=["false", "done", "open"],
                        default="false",
                        help="""La caractéristique des données demandées,
                        par défaut des faux positifs""")

    parser.add_argument("-udi", "--useDevItem",
                        choices=["false", "true", "all"],
                        default="false",
                        help="L utilisation ou non des objets devlopeur")

    # https://stackoverflow.com/questions/15459997/passing-integer-lists-to-python/15460288#15460288
    parser.add_argument("-so", "--source",
                        nargs="+",
                        type=lambda lambda_value: str(lambda_value) if re.match(r"^\*{1}$|^(\d+)(,\d+)*$", str(lambda_value)) else argparse.ArgumentTypeError(f"Invalid source: {str(lambda_value)}"),
                        #new maj 24.10.21 REGEX : "^\*{1}$|^(\d+)(,\d+)*$"
                        default=["*"],
                        help="""La ou les source(s) de la donnée
                        La source 14708 est générique opendata_xref- france     
                        """)

    # https://stackoverflow.com/questions/15459997/passing-integer-lists-to-python/15460288#15460288
    parser.add_argument("-it", "--item",
                        nargs="+",
                        type=int,
                        default=[7170],
                        help="""Le ou les item(s) selectionné(s)
                        Osmose frontend target item, a 4-digit number
                        See https://wiki.openstreetmap.org/wiki/Osmose/issues.
                        La classe 7170 correspond à osmose-backend/analysers/ scripts analyser_merge_road_FR.py, analyser_merge_highway_ref_FR.py
                        """)

    parser.add_argument("-ve", "--verbosity",
                        choices=["DEBUG", "INFO", "WARN"],
                        default="INFO",
                        help="Paramètre de verbosité du niveau de log")

    parser.add_argument("-ts", "--type_signalement",
                        choices=["skip", "test", "submit", "repost"],
                        default="skip",
                        help="""Type de signalement espace co émis.
                        Valeurs parmi
                        test: émission de status=test, aka reçu du serveur EspaceCollaboratif mais non percolé aux collecteurs
                        submit: émission de status=submit, aka reçu du serveur EspaceCollaboratif + percolé aux collecteurs
                        skip: aucun signalement émis, aka le serveur EspaceCollaboratif ne reçoit aucun signalement
                        repost: reprise sur incident pour les issues n'ayant pas fait l'objet d'un signalement""")

    parser.add_argument("-w", "--write_csv",
                        type=bool,
                        default=False,
                        help="""Ecriture d'un csv des issues osmoses
                        requêtées par les paramètres d'exécution du script""")

    # Récupération des arguments
    LOGGER.debug("Recupération des arguments")
    args = parser.parse_args(args)
    osmosecrackerWorkflow.workflow_parameters = str(args)
    LOGGER.info('Arguments: {args}'.format(args=args))

    # Fixation du niveau de log
    if not args.verbosity:
        LOGGER.setLevel(logging.ERROR)
    elif args.verbosity == "WARN":
        LOGGER.setLevel(logging.WARNING)
    elif args.verbosity == "INFO":
        LOGGER.setLevel(logging.INFO)
    elif args.verbosity == "DEBUG":
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.critical("UNEXPLAINED VERBOSITY LEVEL !")
        LOGGER.setLevel(logging.INFO)

    #####
    # Création de la base et instanciation du workflow
    #####
    if not osmosecrackerDatabase.exists():
        osmosecrackerDatabase.create()
    if not osmosecrackerDatabase.is_valid():
        raise osmosecracker_exceptions.DatabaseInvalid("Base invalide.")
        sys.exit("Base invalide.")

    #####
    # Test de la plausabilité des paramètres
    #####
    LOGGER.info("Vérification de la plausabilité des paramètres")
    try:

        # Test web
        LOGGER.debug("Test de la connexion web")
        for url in config.OC_WEBCONNEXION_URLs:
            try:
                requests.get(url,
                            timeout=config.OC_TIMEOUT,
                            proxies=config.OC_PROXIES,
                            headers=config.OC_HEADERS)
                LOGGER.debug("Connected to the Internet from " + url + "    OK")
            except requests.exceptions.ProxyError as exc:
                LOGGER.exception("ERROR 'main' modifie ton fichier de paramètre le proxy n'est pas bon")
                raise
            except requests.ConnectionError as exc:
                LOGGER.exception("ERROR 'main' No internet connection to " + url)
                raise
            except requests.Timeout as exc:
                LOGGER.exception("ERROR 'main' Time OUT, No internet connection to " + url)
                raise
        LOGGER.debug("Test de la connexion web validé")

        for item in args.item:
            if item not in config.OC_ITEM_INFO.keys():
                raise ValueError("ERROR 'main' bad item number")

        # Tester que --country est dans la liste

        # extracte country de l'API 0.3 Osmose
        try:
            url = "https://osmose.openstreetmap.fr/api/0.3/countries"
            response = requests.request("GET",
                                        url,
                                        data=[],
                                        proxies=config.OC_PROXIES,
                                        headers=config.OC_HEADERS)
            countrys = json.loads(response.text)['countries']
        except requests.exceptions.ProxyError as exc:
            LOGGER.exception("ERROR 'main' modifie ton fichier de paramètre le proxy n'est pas bon")
            raise
        except requests.ConnectionError as exc:
            LOGGER.exception("ERROR 'main' No internet connection to " + url)
            raise
        except requests.Timeout as exc:
            LOGGER.exception("ERROR 'main' Time OUT, No internet connection to " + url)
            raise

        for territoire in args.country:
            if territoire in countrys:
                LOGGER.debug(territoire+" est un entrer valide")
            else:
                raise ValueError("ERROR 'main' "
                + str(territoire)+"n'est pas un territoire valide")

        # Tester que start_date est une date,
        # est antérieure à maintenant,
        # est supérieure à 2020/01/01
        if type(args.start_date) == datetime.date:
            if datetime.date.fromisoformat("2020-01-01") < args.start_date:
                LOGGER.debug("start date okay")
            else:
                raise ValueError("ERROR 'main' start date before 2020-01-01")
        else:
            raise ValueError("ERROR 'main' date class is not datetime.date")

        # Tester que en_date est une date,
        # est antérieure ou égale à maintenant,
        # est supérieure à 2020/01/01
        # que start _date est antérieure à end_date
        if type(args.end_date) == datetime.date:
            if args.start_date < args.end_date:
                LOGGER.debug("end date okay")
            else:
                raise ValueError("ERROR 'main' end date before start date")
        else:
            raise ValueError("ERROR 'main' date class is not datetime.date")

        # Source
        # La maj 24.10.21 a mis dans le parsing des arguments une
        # regex sur l'entrée utilisateur --source, rendant obselète sa vérification ici. 
        # En transtypant la liste en set, on enlève les duplicas
        set_source = set(args.source)
        args.source = list(set_source)

        # Tester dep et region valides
        if args.filtredep is not None:
            set_input = args.filtredep
            set_ref = osmosecracker_query_bduni.bduni_get_list_dep()
            if len(list(set(set_input) - set(set_ref))) > 0:
                raise ValueError("ERROR 'main' filtredep unknown")
            del set_input
            del set_ref
        if args.filtrereg is not None:
            set_input = args.filtrereg
            set_ref = osmosecracker_query_bduni.bduni_get_list_reg()
            if len(list(set(set_input) - set(set_ref))) > 0:
                raise ValueError("ERROR 'main' filtrereg unknown")
            del set_input
            del set_ref
        
    except Exception as exc:
        LOGGER.exception("plausabilité des paramètres")
        raise
    LOGGER.info("Vérification de la plausabilité des paramètres terminée")

    # Si pas reprise sur incident des signalements
    if (not args.type_signalement == "repost"):
        #####
        # Requête Osmose des issues
        #####
        LOGGER.info("Requêtes OSMOSE")
        osmosecrackerWorkflow.timestamp_issues_collecting_start = (
            datetime.datetime.now())
        osmose_issues: list(osmosecracker_issue.OsmoseCrackerIssue) = []
        osmose_issues_new: list(osmosecracker_issue.OsmoseCrackerIssue) = []
        if not args.espace_co_statuses_only:
            try:
                # Requête sur l'api osmose 0.3
                # avec pour querystring les données d'entré du programme
                for geo_selecte in args.country:
                    for source_selecte in args.source:
                        for item_selecte in args.item:
                            for classe in config.OC_ITEM_INFO[item_selecte]['classe'].keys():
                                liste_issues = (
                                    osmosecracker_query_osmose.extracte_osmose(
                                        config.OC_LIMIT,
                                        geo_selecte,
                                        config.OC_FULL,
                                        args.status,
                                        args.start_date,
                                        args.end_date,
                                        args.useDevItem,
                                        source_selecte,
                                        classe,
                                        item_selecte))
                                LOGGER.info("Le script conduit à obtenir {0} issues sur le territoire {1} source {2} item {3} classe {4}. ".format(
                                    len(liste_issues),
                                    geo_selecte,
                                    source_selecte,
                                    item_selecte,
                                    classe))
                                for issue in liste_issues:
                                    if issue not in osmose_issues:
                                        osmose_issues.append(issue)
                                        alreadyknownissue = osmosecrackerDatabase.get_issue_by_osmose_uuid(issue.core_id)
                                        sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
                                        if alreadyknownissue is None:
                                            osmose_issues_new.append(issue)
                LOGGER.debug("osmose_issues okay, n={0}".format(len(osmose_issues)))
                LOGGER.info("Le script conduit à obtenir {0} issues. ".format(len(osmose_issues)))
                osmosecrackerWorkflow.stats_issues_collected_count = len(osmose_issues)
                LOGGER.info("Sur ces {0} issues, {1} sont inconnues d'OsmoseCracker.".format(len(osmose_issues), len(osmose_issues_new)))
                osmosecrackerWorkflow.stats_issues_collected_new_count = len(osmose_issues_new)

                # Requête sur l'api osmose 0.3
                # a partir des uuid extrete des objet dans liste d'objet 'osmose_issues_new'
                LOGGER.info("Requêtes complémentaires UUID")
                for obj_select in osmose_issues_new:
                    obj_select.update_with_uuid()
                    sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
                LOGGER.debug("update_with_uuid okay")
                osmosecrackerWorkflow.timestamp_details_uuid_added = (
                    datetime.datetime.now())
                LOGGER.info("Fin Requêtes complémentaires UUID")

            except Exception as exc:
                LOGGER.exception("Requêtes Osmose")
                raise
        LOGGER.info("Requêtes OSMOSE terminées, nouvelle issue n={0}".format(len(osmose_issues_new)))
      

        #####
        # Requête complémentaires BDUni table "commune"
        #####
        LOGGER.info("Requêtes complémentaires BDUni")
        obj_in_filtre = 0
        for obj_select in osmose_issues_new:
            flag = False
            obj_select.bduni_collect_commune()
            if ((args.filtredep is None) and (args.filtrereg is None)):
                flag = True
            if args.filtredep is not None:
                if obj_select.bduni_departement_code_insee in args.filtredep:
                        flag = True
            if args.filtrereg is not None:
                if obj_select.bduni_region_code_insee in args.filtrereg:
                    flag = True
            if flag:
                obj_in_filtre += 1
            sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
        
        LOGGER.info("Requêtes complémentaires code INSEE BDUni terminées")
        LOGGER.info("{0} objet(s) correspondant au filtre spatial demandé".format(obj_in_filtre))


        #####
        # Collecte de données et Persistance SQLite selon filtre spatial le cas échéant
        #####
        LOGGER.info("Persistance SQLite et requètes complemetaire")
        n=0 # NB future signalement
        if args.status == "false" and not args.espace_co_statuses_only:
            if osmosecrackerDatabase.is_valid():
                for obj_select in osmose_issues_new:
                    flag = False
                    if ((args.filtredep is None) and (args.filtrereg is None)):
                        flag = True
                    if args.filtredep is not None:
                        if obj_select.bduni_departement_code_insee in args.filtredep:
                            flag = True
                    if args.filtrereg is not None:
                        if obj_select.bduni_region_code_insee in args.filtrereg:
                            flag = True
                    if flag:
                        #####
                        # Requête complémentaires BDUni
                        #####
                        try:
                            obj_select.bduni_collect_complement()
                        except Exception as exc:
                            LOGGER.exception("Requêtes complémentaires BDUni")
                            raise

                        LOGGER.debug("Requêtes complémentaires BDUni de l'Issue Osmose terminées")

                        #####
                        # Requêtes complémentaires OSM
                        #####
                        #LOGGER.info("Requêtes complémentaires OSM")
                        # TODO dans une future V2
                        # rechercher pour chaque- issue osmose dans obj_select in osmose_issues_new:
                        # l'objet OSM correspondant si cet objet existe
                        #LOGGER.info("Requêtes complémentaires OSM terminées")

                        
                        
                        #####
                        # Persistance en base OSMOSECRACKER
                        #####
                        osmosecrackerDatabase.insert(obj_select)
                        LOGGER.debug("Issue Osmose insérée en base")
                        n+=1
                    else:
                        LOGGER.debug("Issue Osmose non insérée en base")
                    sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
        else:
            LOGGER.info("Les issues Osmose requêtées sont celles de status={0}"
                        "Aucune persistance à effectuer".format(
                            args.status
                        ))
        LOGGER.info("Persistance SQLite terminée, {0} nouvelles issues Osmose correspondant au filtre spatial demandé persistées".format(n))
        
        osmosecrackerWorkflow.timestamp_issues_collecting_end = (
            datetime.datetime.now())
        
        del n

    #####
    # Verife Statue des zicad
    #####
    LOGGER.info("Mise à jour des Zicad ")
    # on interroge la base sqlite pour chercher les inzicad non renseignés
    issuesZicadrefresh: List[osmosecracker_issue.OsmoseCrackerIssue] = (
        osmosecrackerDatabase.get_issues_where_zicad_null())
    LOGGER.info("Le script conduit à obtenir {0} issues où ZICAD null. ".format(len(issuesZicadrefresh)))
    # on recupere une liste d'issue où l'information inzicad est renseignée
    issuesZicadrefreshed: List[osmosecracker_issue.OsmoseCrackerIssue] = osmosecracker_query_bduni.is_in_zicad(issuesZicadrefresh)
    LOGGER.info("Sur ces {0} issues, {1} sont caractérisées.".format(len(issuesZicadrefresh), len(issuesZicadrefreshed)))
    # on met à jour la base sqlite pour chaqune de ces issue
    for obj_select in issuesZicadrefreshed:
        # On met à jour SQLite pour l'objet selected
        osmosecrackerDatabase.update_zicad(obj_select)
        sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
    LOGGER.info("Sur ces {0} issues, {1} sont caractérisées et cette info persistée.".format(len(issuesZicadrefresh), len(issuesZicadrefreshed)))
    del issuesZicadrefresh
    del issuesZicadrefreshed
    LOGGER.info("Mise à jour des zicad terminée")

    #####
    # Signalements EspaceCollaboratif
    #####
    LOGGER.info("Signalements EspaceCollaboratif")
    if (not args.type_signalement == "skip"):
        issuesSignalement: list(osmosecracker_issue.OsmoseCrackerIssue) = (
            osmosecrackerDatabase.get_issues_by_espacecosignalements_none_and_zicad_false())
        LOGGER.info("Localement, {0} objets Osmose n'ont pas fait l'objet d'un "
                    "signalements EspaceCollaboratif".format(
                        str(len(issuesSignalement))))
        issuesSignalementTimestamp = datetime.datetime.now()
        if args.status == "false":
            if osmosecrackerDatabase.is_valid():
                signalementid = None
                reportcounter = 0
                
                #####
                # Clustering
                #####
                issuesSignalement_cluster: List[osmosecracker_issue.OsmoseCrackerIssue] = osmosecracker_query_bduni.clustering(issuesSignalement)
                
                cluster_id = None 
                signalementid = None
                for issue in issuesSignalement_cluster:
                    try:   
                        #####
                        # Génération du rapport markdown
                        #####
                        try:
                            issue.markdown_report()
                        except Exception as exc:
                            LOGGER.exception("Génération du rapport markdown")
                            raise

                        LOGGER.debug("Raport Markdown Issue Osmose terminées")

                        #####
                        # Emission du signalement 
                        #####

                        if issue.cluster_id is not None:  # Vérifier s'il y a un identifiant de cluster
                            if issue.cluster_id != cluster_id:  # Vérifier si l'identifiant de cluster est différent du précédent
                                reportcounter += 1
                                cluster_id = issue.cluster_id
                                #" Nouveau signalement de cluster détecté "
                                signalementid = osmosecracker_espacecollaboratifign.post_signalement(
                                            lon=issue.core_lon,
                                            lat=issue.core_lat,
                                            message=issue.details_descriptionstr
                                            +"\n "
                                            +"**Attention : ce signalement englobe une zone. Vous pouvez trouver cette zone sur la géométrie affichée ci-contre.**"
                                            +"\n ",
                                            theme=issue.espaceco_theme,
                                            type_signalement=args.type_signalement,
                                            sketchcontent=issue.sketchcontent)
                                LOGGER.debug(signalementid)
                            else:
                                # signalement dans un clusteur qui a deja fait l'objet d'un signalement
                                signalementid = -abs(signalementid)
                                LOGGER.debug(signalementid)
                        else:
                            #Traitement pour un signalement classique sans cluster
                            reportcounter += 1
                            signalementid = osmosecracker_espacecollaboratifign.post_signalement(
                                            lon=issue.core_lon,
                                            lat=issue.core_lat,
                                            message=issue.details_descriptionstr,
                                            theme=issue.espaceco_theme,
                                            type_signalement=args.type_signalement)
                            LOGGER.debug(signalementid)
                        if signalementid is not None:
                                        issue.espaceco_signalement_id = signalementid
                                        issue.espaceco_signalement_status_refresh_timestamp = issuesSignalementTimestamp
                                        if signalementid > 0 : # Objet ne faisant pas partie d’un cluster ou objet 'principal' du cluster 
                                            issue.espaceco_signalement_status = args.type_signalement
                                        else : #  Objet secondaire d’un cluster (le signalement a déjà été émis par un autre objet)
                                            issue.espaceco_signalement_status = None
                                        osmosecrackerDatabase.update_signalement(issue)
                                        LOGGER.info("Signalement créé {0} / {1}, id {2}".format(
                                            reportcounter,
                                            len(issuesSignalement),
                                            signalementid))
                                        osmosecrackerWorkflow.stats_issues_reported_count = reportcounter
                                        sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
                    except Exception as exc:
                        LOGGER.exception("Signalements EspaceCollaboratif")
                        raise
            #TODO END NEW V1.1
        else:
            LOGGER.info("Les issues Osmose requêtées sont celles de status={0}"
                        "Aucun signalement EspaceCollaboratif à effectuer".format(
                            args.status
                        ))
    else:
        LOGGER.info("Pas de Signalements EspaceCollaboratif effectuer")
    LOGGER.info("Signalements EspaceCollaboratif terminés")

    #####
    # Rafraichissement des status
    #####
    LOGGER.info("Mise à jour des statuts de signalement EspaceCollaboratif")
    issuesStatusrefresh: list(osmosecracker_issue.OsmoseCrackerIssue) = (
        osmosecrackerDatabase.get_issues_by_espacecosignalements_unclosed())
    LOGGER.info("Le script conduit à obtenir {0} issues où le status du signalement est à rafraichir.".format(len(issuesStatusrefresh)))
    issuesStatusrefreshTimestamp = datetime.datetime.now()
    for obj_select in issuesStatusrefresh:
        obj_select.espaceco_signalement_status = osmosecracker_espacecollaboratifign.get_status_signalement(obj_select.espaceco_signalement_id)
        obj_select.espaceco_signalement_status_refresh_timestamp = issuesStatusrefreshTimestamp
        if obj_select.espaceco_signalement_status != None:
            osmosecrackerDatabase.update_signalement(obj_select)
        sleep(1) # Attendre 1s pour être plus sympa avec les serveurs
    LOGGER.info("Mise à jour des statuts de signalement EspaceCollaboratif terminée")

    #####
    # Ecriture des issues selon le paramétrage, si demandé
    #####
    if args.write_csv:
        LOGGER.info("Ecriture du csv")
        try:
            osmose_issues_csv: list(osmosecracker_issue.OsmoseCrackerIssue) = []
            for issue in osmose_issues:
                alreadyknownissue = osmosecrackerDatabase.get_issue_by_osmose_uuid(issue.core_id)
                if alreadyknownissue is None:
                    osmose_issues_csv.append(issue)
                else:
                    osmose_issues_csv.append(alreadyknownissue)
            LOGGER.debug(len(osmose_issues_csv))
            with open(pathlib.Path(__file__).resolve().parent.joinpath(
                'issues_{status}_{timestamp}.csv'.format(
                    status=args.status,
                    timestamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))),
                    "w") as f:
                w = DataclassWriter(f, osmose_issues_csv, osmosecracker_issue.OsmoseCrackerIssue)
                w.write(skip_header=False)
        except Exception as exc:
            LOGGER.exception("Ecriture du csv")
            raise
        else:
            LOGGER.info("Ecriture du csv terminée")


if __name__ == "__main__":
    LOGGER.info("Début du programme OsmoseCracker")
    from osmosecracker_workflow import osmosecrackerWorkflow
    try:
        main(sys.argv[1:])
        osmosecrackerWorkflow.timestamp_workflow_end = (
            datetime.datetime.now())
        osmosecrackerWorkflow.workflow_duration_seconds = math.ceil(
            (osmosecrackerWorkflow.timestamp_workflow_end
             - osmosecrackerWorkflow.timestamp_workflow_start).total_seconds())
        LOGGER.info("Fin d'exécution du programme OsmoseCracker SANS erreur")
    except Exception as exc:
        osmosecrackerWorkflow.log_error(repr(exc))
        sys.exit(1)  # An unsuccessful exit can be signaled by passing a value other than 0 or None.
    except SystemExit:
        LOGGER.info("Fin d'exécution du programme OsmoseCracker AVEC erreur")
    else:
        sys.exit(0)  # An successful exit can be signaled by passing a value = 0.
