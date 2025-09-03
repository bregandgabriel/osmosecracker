#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# version ='1.1'
# ---------------------------------------------------------------------------
"""
Fonctions de requête de l'API Osmose

Note 
----
Doc OSMSOE:
https://wiki.openstreetmap.org/wiki/Osmose/api/0.3
/!\ Attention la doc OSMSOSE n'est pas complète /ꬷ\ 
"""
# ---------------------------------------------------------------------------

# Notes

# Imports

import argparse
import datetime
import json
import logging
import sys
import requests
import uuid
import osmosecracker_config as config
import osmosecracker_issue

LOGGER = logging.getLogger('OsmoseCracker.Query.Osmose')


###
# extracte generale osmose
###


def extracte_osmose(limit,
                    country,
                    full,
                    status,
                    startedate,
                    endate,
                    useDevItem,
                    source,
                    classe,
                    item) -> "osmosecracker_issue.OsmoseCrackerIssue":
    """Fonction d'appel à l'API Osmose.

    Keyword arguments:
        limit (string): Returned issues, 10000 max
        country (string): Issues for an area. The wildcard "*" is allowed
        as part of the parameter, eg "france*" for all regions at once. See
        the list at http://osmose.openstreetmap.fr/api/0.3/countries
        full (string): Détail des erreurs false | true
        status (string): Issues status, "open", "done" for issues reported as
        corrected and "false" for issues repported as false positive.
        startedate (string): Issues generated after this date. For statistics
        begins on this date. Date format "Y[-m[-d]]".
        endate (string): Issues generated before thit date. For statistics
        ended on this date. Date format "Y[-m[-d]]".
        useDevItem (string): Returns issues only for items that are not
        active, not active are dev or buggy items.
        source (string): Number of the source, see the source list at
        http://osmose.openstreetmap.fr/fr/control/update
        classe (string): Classes of item, one or many classes separated with
        commas, a class is a sub part of an item. Make sense only with a
        unique item.
        item (string): Returned items list, a number followed by "xxx" for
        complet category. See the list at
        http://osmose.openstreetmap.fr/fr/api/0.2/meta/items

    Returns:
        Liste d'instances osmosecracker_issue.OsmoseCrackerIssue
    """
    try:
        LOGGER.debug("extracte_osmose")
        sous_liste_issues = []
        url = "https://osmose.openstreetmap.fr/api/0.3/issues.json"
        # Appel à l'API OSMOSE 0.3 sous forme d'une requête GET
        # en demandant les données au format json
        querystring = {
            "limit": limit,
            "country": str(country)+"*",
            "full": full,
            "status": status,
            "start_date": startedate,
            "end_date": endate,
            "useDevItem": useDevItem,
            "source": source,
            "class": classe,
            "item": item}
        LOGGER.debug(querystring)
        # les Query utilisent les données entrées dans les variables définies
        # (les variables 'full' et 'status' sont toujours les mêmes)

        # Appel serveur
        response = requests.request("GET",
                                    url,
                                    timeout=config.OC_TIMEOUT,
                                    proxies=config.OC_PROXIES,
                                    params=querystring,
                                    headers=config.OC_HEADERS)
        LOGGER.info(response.url)
        # Trasformation en json pour une bonne exploitation des données
        response = response.json()

        # Parcour les données du json
        for rep in response['issues']:
            # Insertion des information dans
            # un nouvelle objet ajouté a la liste d'objet
            form = '%Y-%m-%d %H:%M:%S%z'
            new_issue = osmosecracker_issue.OsmoseCrackerIssue(
                uuid=rep['id'],
                status=status,
                source=rep['source'],
                item=rep['item'],
                item_name_auto=config.OC_ITEM_INFO[int(item)]['name_en'],
                item_name_fr=config.OC_ITEM_INFO[int(item)]['name_fr'],
                classe=rep['class'],
                class_name_auto=config.OC_ITEM_INFO[int(item)]['classe'][int(classe)]['titre_en'],
                class_name_fr=config.OC_ITEM_INFO[int(item)]['classe'][int(classe)]['titre_fr'],
                level=rep['level'],
                subtitle=str(rep['subtitle']['auto']) if rep['subtitle'] else None,
                country=country,
                # analyser=rep['uuid'],
                # doesn't existe
                timestamp=datetime.datetime.strptime(rep['update'], form),
                username=','.join(a for a in rep['usernames']),
                lat=float(rep['lat']),
                lon=float(rep['lon']),
                elems=json.dumps(rep['osm_ids'], indent=4),
                espaceco_theme=config.OC_ITEM_INFO[int(item)]['theme_espace_co_ign'],
                core_classe_bduni=config.OC_ITEM_INFO[int(item)]['classe_bduni'])
            if new_issue.core_osm_ids_elems is not None:
                json_as_dict = json.loads(new_issue.core_osm_ids_elems)
                new_issue.core_osm_ids_nodes = json_as_dict['nodes'] if 'nodes' in json_as_dict else None
                new_issue.core_osm_ids_ways = json_as_dict['ways'] if 'ways' in json_as_dict else None
                new_issue.core_osm_ids_relations = json_as_dict['relations'] if 'relations' in json_as_dict else None
            sous_liste_issues.append(new_issue)        
        return sous_liste_issues
    except Exception as exc:
        try:
            # Teste à l'API OSMOSE 0.3 verification bon fonctionnement
            # des serveurs avec des parametre prédefini
            querystring = {
                "limit": 1,
                "country": "france*",
                "full": "true",
                "status": "false",
                "start_date": "2023-02",
                "end_date": "2023-03",
                "useDevItem": "false",
                "source": 14708,
                "class": 1}
            response = requests.request("GET",
                                        url,
                                        timeout=config.OC_TIMEOUT,
                                        proxies=config.OC_PROXIES,
                                        params=querystring,
                                        headers=config.OC_HEADERS)
        except requests.exceptions.ProxyError as exc:
            raise Exception("""ERROR 'extracte_osmose'
            modifie ton fichier de paramètre le proxy n'est pas bon""")
        except requests.ConnectionError as exc:
            raise Exception("""ERROR 'extracte_osmose'
              No internet connection to """+url)
        except requests.Timeout as exc:
            raise Exception("""ERROR 'extracte_osmose'
              Time OUT, No internet connection to """+url)
        # Sinon
        raise Exception("ERROR from 'extracte_osmose' bad data input "
                        + str(exc))


###
# extracte avec UUID osmose
###


def extracte_osmose_uuid(uuid) -> json:
    """Fonction d'appel à l'API Osmose, pour un uuid donné.

    Keyword arguments:
        uuid (string): L'incohérence Osmose à requêter

    Returns:
        json Osmose de l'incohérence
    """
    try:
        url = ("https://osmose.openstreetmap.fr/api/0.3/false-positive/"
               + str(uuid))
        # Appel à l'API OSMOSE 0.3 sous forme d'une requête GET
        # des données liée a un faux positif trouvé grace à un UUID
        response = requests.request("GET",
                                    url,
                                    timeout=config.OC_TIMEOUT,
                                    proxies=config.OC_PROXIES,
                                    headers=config.OC_HEADERS)
        response = response.json()
        return response
    except Exception as exc:
        try:
            # Teste à l'API OSMOSE 0.3 verification bon fonctionnement
            # des serveur avec des parametre prédefini
            id = "45ffa954-6475-1598-a6e5-15c03c01f98e"
            url = """https://osmose.openstreetmap.fr/api/0.3/false-positive/"""
            url = url + id
            response = requests.request("GET",
                                        url,
                                        timeout=config.OC_TIMEOUT,
                                        proxies=config.OC_PROXIES,
                                        headers=config.OC_HEADERS)
        except requests.exceptions.ProxyError as exc:
            raise Exception("""ERROR 'extracte_osmose_uuid'
             modifie ton fichier de paramètre le proxy n'est pas bon""")
        except requests.ConnectionError as exc:
            raise Exception("""ERROR 'extracte_osmose_uuid'
            No internet connection to """ + url)
        except requests.Timeout as exc:
            raise Exception("""ERROR 'extracte_osmose_uuid' Time OUT,
            No internet connection to """ + url)
        # Sinon
        else:
            raise Exception("ERROR from 'extracte_osmose_uuid' bad data input "
                            + repr(exc))


def item_and_class_info(items: int, classe: int):
    """Fonction d'appel à l'API Osmose, pour documenter un couple item/classe.

    Keyword arguments:
        items (int): Le groupe d'erreur à considérer
        classe (int): La classe d'un groupe d'erreur à considérer

    Returns:
        tuple contenant le nom de l'item et celui de la classe
    """
    try:
        url = ("http://osmose.openstreetmap.fr/api/0.3/items/"
               + str(items) +
               "/class/"
               + str(classe) +
               "?langs=auto")
        response = requests.request("GET",
                                    url,
                                    timeout=config.OC_TIMEOUT,
                                    proxies=config.OC_PROXIES,
                                    headers=config.OC_HEADERS)
        response = response.json()
        name_item = response['categories'][0]['items'][0]['title']['auto']
        name_class_error = (
            response['categories'][0]['items'][0]['class'][0]['title']['auto'])
        return [name_item, name_class_error]
    except Exception as exc:
        try:
            url = ("http://osmose.openstreetmap.fr/api/0.3/items/"
                   + 7170 +
                   "/class/"
                   + 1 +
                   "?langs=auto")
            response = requests.request("GET",
                                        url,
                                        timeout=config.OC_TIMEOUT,
                                        proxies=config.OC_PROXIES,
                                        headers=config.OC_HEADERS)
        except requests.exceptions.ProxyError as exc:
            raise Exception("""ERROR 'item_and_class_info'
             modifie ton fichier de paramètre le proxy n'est pas bon""")
        except requests.ConnectionError as exc:
            raise Exception("""ERROR 'item_and_class_info'
              No internet connection to """+url)
        except requests.Timeout as exc:
            raise Exception("""ERROR 'item_and_class_info'
              Time OUT, No internet connection to """+url)
        # Sinon
        raise Exception("ERROR from 'item_and_class_info' bad data input "
                        + str(exc))
