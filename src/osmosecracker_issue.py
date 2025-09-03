#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# Modif Date v1.1 : July 2024
# version ='1.1'
# ---------------------------------------------------------------------------
"""
Cette partie crée la classe d'objet qui sera utilisée 
tout au long du programme pour stocker en mémoire 
toutes les informations qui nous sont utiles,
puis les persiste en base SQLite.
Des instances sont créees pour:
_chaque incohérence Osmose correspondant au(x) filtre(s)
de lancement d'OsmoseCracker
_reprendre/actualiser les statuts de signalement

Parameters
----------
Data : all
    Toutes les données liées à un objet.

Returns
-------
Data : all
    Modifie certaines données pour en créer d'autres.

Note
----
Pour ajouter une donnée, suivez ces étapes :
- Modifiez les '# variables de l'objet'
- Ajoutez-la à _init_ : self.newdata = None
"""
# ---------------------------------------------------------------------------

# Notes

# Imports
from dataclasses import dataclass, field
import datetime
import logging
import urllib.parse
import osmosecracker_config as config
import osmosecracker_query_osmose
import osmosecracker_query_bduni

LOGGER = logging.getLogger('OsmoseCracker.Issue')

####
# création de la class
####


@dataclass(init=False, repr=False, eq=True,
           order=False, unsafe_hash=False, frozen=False)
class OsmoseCrackerIssue(object):
    """Une classe responsable de véhiculer les informations concernant
    une incohérence Osmose."""

    ####
    # variable de l'oject
    ####

    # FROM 'extracte_osmose'

    core_id: str = field(
        init=True,  compare=True)
    """ ID

    Identifiant unique de l'objet OSMOSE,
    plus d'information disponible sur
    "https://wiki.openstreetmap.org/wiki/ID".
    Nous l'utilisons donc comme clé primaire pour OSMOSECRACKER"""

    core_status: str = field(
        init=True,  compare=True)
    """ Statut de signalement OSMOSE [false, done, open]

    Les statuts permettent de savoir l'état du signalement
    OSMOSE : "open" (pas encore traité) et "done"
    (changement effectué sur la base OSM) ne nous concernent
    pas. Nous recherchons des fausses positives,
    celles-ci ont un statut "false" """

    core_lat: float = field(
        init=True,  compare=False)
    """ Latitude de l'objet en EPSG:4326 (WGS84) """

    core_lon: float = field(
        init=True, compare=False)
    """ Longitude de l'objet en EPSG:4326 (WGS84) """

    core_item_id: int = field(
        init=True, compare=False)
    """Numéro de l'item OSMOSE

    Tous les items OSMOSE ont un identifiant.
    Vous pouvez vous référer au lien suivant
    pour plus d'informations à leur sujet :
    "https://wiki.openstreetmap.org/wiki/Osmose/issues" """

    core_item_name_auto: str = field(
        init=True, compare=False)
    """ Nom EN de l'item OSMOSE """

    core_item_name_fr: str = field(
        init=True, compare=False)
    """ Nom FR de l'item OSMOSE

    Le nom français des items qui nous
    intéressent n'est pas toujours référencé.
    Nous avons donc lié chaque item ID à un
    nom français pour la future création de signalement """

    core_class_id: int = field(
        init=True, compare=False)
    """ Numéro de l'erreur liée à l'item

    Chaque item a un certain nombre d'erreurs
    qui lui sont liées, et chacune d'elles
    a un numéro. Il convient cependant de
    noter que deux classes peuvent avoir le
    même numéro sans avoir de lien entre
    elles, tant que l'item auquel elles sont
    liées est différent """

    core_class_name_auto: str = field(
        init=True, compare=False)
    """ Nom EN de l'erreur OSMOSE """

    core_class_name_fr: str = field(
        init=True, compare=False)
    """ Nom FR de l'erreur OSMOSE

    Le nom en français des classes d'erreur
    qui nous intéressent n'étant pas toujours
    référencé, nous avons associé chaque identifiant
    de classe (lié à un identifiant d'item) à un
    nom français en vue de la future création
    de signalements """

    core_subtitle: str = field(
        init=True, compare=False)
    """ Informations complémentaires sur l'erreur

    Ce texte fournit des informations
    complémentaires sur le signalement OSMOSE.
    Cependant, la qualité des subtitle est varriable """

    core_country: str = field(
        init=True, compare=False)
    """ Zone de provenance (france* par défaut)

    La zone de provenance des données est la zone géographique
    sur laquelle nous avons effectué un filtre lors
    de l'appel au serveur OSMOSE, ici la france*.
    Cela permet de sélectionner les données de toute
    la France """

    # new description maj 24.10.21
    core_source: int = field(
        init=True, compare=False)
    """ Numéro de la source

    #https://github.com/osm-fr/osmose-backend/issues/2363#issuecomment-2419752834
    La source est la combinaison de "l'analyser" utilisée
    pour la comparaison de la donnée OSM et de la donnée externe,
    ainsi que la zone géographique de la donnée.
    Cependant, cette dernière est très peu documentée
     """

    core_level: int = field(
        init=True, compare=False)
    """ Niveau de gravité de l'erreur entre 1 et 3 """

    core_usernames: str = field(
        init=True, compare=False)
    """ Nom de l'utilisateur qui a modifié en dernier
    un objet OSM (NULL par défaut)

    Jamais renseigné par défaut car nous traitons
    des objets OSMOSE et non OSM """

    core_update_timestamp: datetime.datetime = field(
        init=True, compare=False)
    """ Date du lancement du programme OSMOSE 
    pour la création des signalements OSM """

    core_osm_ids_elems: str = field(
        init=True, compare=False)
    """ Info Osmose sur nodes, way et relation """

    # FROM 'xxxxxxx'

    core_osm_ids_nodes: str = field(
        init=False, compare=False)
    """ Noeuds osm de l'objet """

    core_osm_ids_ways:  str = field(
        init=False, compare=False)
    """ Passages osm de l'objet """

    core_osm_ids_relations: str = field(
        init=False, compare=False)
    """ Relations osm de l'objet """

    # FROM  'markdown_report'

    details_descriptionstr: str = field(
        init=False, compare=False)
    """ Résumé (créé) au format Markdown des
    données pour le signalement espace co

    À partir de toutes les données récoltées,
    nous créons un rapport Markdown à l'intention
    des lecteurs des signalements que OSMOSECRACKER
    crée. Ce rapport filtre les données utiles et
    crée un signalement dans un format fixe pour
    permettre une meilleure compréhension de celui-ci """

    # FROM  'extracte_osmose_uuid'

    details_minlat: float = field(
        init=False, compare=False)
    """ Zoom maximal prédéfini pour l'application
    Osmose sur l'issue

    latitude minimale de la Bbox """

    details_maxlat: float = field(
        init=False, compare=False)
    """ Zoom maximal prédéfini pour l'application
    Osmose sur l'issue

    latitude maximale de la Bbox """

    details_minlon: float = field(
        init=False, compare=False)
    """ Zoom maximal prédéfini pour l'application
    Osmose sur l'issue

    longitude minimale de la Bbox """

    details_maxlon: float = field(
        init=False, compare=False)
    """ Zoom maximal prédéfini pour l'application
    Osmose sur l'issue

    longitude maximale de la Bbox """

    details_b_date_datetime: datetime.datetime = field(
        init=False, compare=False)
    """ Date du signalement OSMOSE

    Date à laquelle OSMOSE a comparé les données
    IGN aux données OSM et a créé un signalement
    s'il y avait une incohérence entre les deux """

    # FROM  'xxxxxxx'

    details_osm_json_nodes: str = field(
        init=False, compare=False)
    """ Noeuds osm de l'objet, détails """

    details_osm_json_ways: str = field(
        init=False, compare=False)
    """ Passages osm de l'objet, détails  """

    details_osm_json_relations: str = field(
        init=False, compare=False)
    """ Relations osm de l'objet, détails """

    details_new_elemns: str = field(
        init=False, compare=False)
    """ Nouveau element liée a l'objet """

    # FROM  'xxxxxxx'

    osm_objects: str = field(
        init=False, compare=False)
    """ Objet OSM liée a l'objet OSMOSE [En dévlopement] """

    # FROM 'xxxxxxx'

    bduni_zone_collecte_collecteur: str = field(
           init=False, compare=False)
    """ Collecteur lié à la zone géographique de la BDuni
    où l'objet BDuni lié à l'objet OSMOSE a été collecté """

    espaceco_theme: str = field(
        init=False, compare=False)
    """ Objet BDuni lié à l'objet OSMOSE """

    bduni_commune_code_insee: str = field(
        init=False, compare=False)
    """ ID INSEE BDuni de la commune  """

    bduni_commune_nom_officiel: str = field(
        init=False, compare=False)
    """ Nom BDuni de la commune """

    bduni_canton_code_insee: str = field(
        init=False, compare=False)
    """ ID INSEE BDuni du canton

    Plus d'information :
    *********"""

    bduni_arrondissement_code_insee: str = field(
        init=False, compare=False)
    """ ID INSEE BDuni de l'arrondissement

    Plus d'information :
    *********"""

    bduni_arrondissement_nom_officiel: str = field(
        init=False, compare=False)
    """ Nom BDuni de l'arrondissement """

    bduni_collectivite_terr_code_insee: str = field(
        init=False, compare=False)
    """ ID INSEE BDuni de la collectivité territorial

    Plus d'information :
    *********"""

    bduni_collectivite_terr_nom_officiel: str = field(
        init=False, compare=False)
    """ Nom BDuni de la collectivité territoria """

    bduni_departement_code_insee: str = field(
        init=False, compare=False)
    """ ID INSEE du departement

    Plus d'information :
    *********"""

    bduni_departement_nom_officiel: str = field(
        init=False, compare=False)
    """ Nom du departement """

    bduni_region_code_insee: str = field(
        init=False, compare=False)
    """ ID INSEE BDuni de la region
    Plus d'information :
    *********"""

    bduni_region_nom_officiel: str = field(
        init=False, compare=False)
    """ Nom BDuni de la region """

    bduni_territoire_nom: str = field(
        init=False, compare=False)
    """ Type de Territoire """

    bduni_territoire_srid: int = field(
        init=False, compare=False)
    """ Code EPSG du système de projection
    légal du territoire bduni_territoire_nom """

    bduni_x: float = field(
        init=False, compare=False)
    """ Coordonnée X, système de projection
    légal du territoire bduni_territoire_nom """

    bduni_y: float = field(
        init=False, compare=False)
    """ Coordonnée Y, système de projection
    légal du territoire bduni_territoire_nom """

    bduni_object_cleabs: str = field(
        init=False, compare=False)
    """ ID objet Bduni """

    bduni_objet_attribut_1: str = field(
        init=False, compare=False)
    """ SELECT BDuni atribut1 """

    bduni_objet_attribut_2: str = field(
        init=False, compare=False)
    """ SELECT BDuni atribut2 """

    bduni_objet_attribut_3: str = field(
        init=False, compare=False)
    """ SELECT BDuni atribut3 """

    bduni_objet_attribut_4: str = field(
        init=False, compare=False)
    """ SELECT BDuni atribut4"""

    bduni_objet_attribut_5: str = field(
        init=False, compare=False)
    """ SELECT BDuni atribut5 """

    bduni_zicad: bool = field(
        init=False, compare=False)
    """ Dans une ZICAD ou non

    Vérification que l'objet ne soit pas
    dans une ZICAD pour ne pas créer un
    signalement inutile"""

    core_classe_bduni: str = field(
        init=True, compare=False)
    """ Classe de l'objet dans la BDuni """

    bduni_objet_date_modification: str = field(
        init=False, compare=False)
    """ Date non actualisé de la derniere
    modification de l'objet en Bdunu

    à chaque lancement de OSMOSECRACKER
    cette information n'est pas mise a jour en raison
    que les information contenue dans le suivi d'OSMOSECRACKER
    liée a la Bduni na pas vocation a etre mis a jour.
    Pour plus d'information :
    *********"""

    # FROM 'clustering'
    #TODO NEW V1.1
    cluster_id: str = field(
        init=False, compare=False)
    """  id global du cluster
    concatenation :
        - core_item_id
        - core_class_id
        - bduni_objet_attribut_1
        - raw_cluster_id (num cluster) """

    sketchcontent: dict = field(
            init=False, compare=False)
    """ descriptif du cluster (geometrie) 
    selon le format sketch de l espace co """

    # FROM 'xxxxxxx'

    espaceco_signalement_id: int = field(
        init=False, compare=False)
    """ ID Espaceco du signalement de l'objet  """

    espaceco_signalement_status: str = field(
        init=False, compare=False)
    """ Statut Espaceco du signalement de l'objet  """

    espaceco_signalement_status_refresh_timestamp: str = field(
        init=False, compare=False)
    """ Date du dernier rafraichissement de statut Espaceco du signalement de l'objet """

    ####
    # def du init
    ####

    def __init__(self,
                 uuid: str,
                 status: str,
                 source: int,
                 item: int,
                 item_name_auto: str,
                 item_name_fr: str,
                 classe: int,
                 class_name_auto: str,
                 class_name_fr: str,
                 level: int,
                 subtitle: str,
                 country: str,
                 timestamp: datetime.datetime,
                 username: str,
                 lat: float,
                 lon: float,
                 elems: str,
                 espaceco_theme: str,
                 core_classe_bduni: str):
        """Crée et initialise l'instance de
        osmosecracker_issue.OsmoseCrackerIssue.

        Keyword arguments:
        uuid (string):
        status (string):
        source (int):
        item (int):
        item_name_auto (string):
        item_name_fr (string):
        classe (int):
        class_name_auto (string):
        class_name_fr (string):
        level (int):
        subtitle (string):
        country (string):
        timestamp (datetime.datetime):
        username (string):
        lat (float):
        lon (float):
        elems (string):
        espaceco_theme (string):
        classe_bduni (string):

        Returns:
            Instance osmosecracker_issue.OsmoseCrackerIssue
        """
        self.core_id = uuid
        self.core_status = status
        self.core_source = source
        self.core_item_id = item
        self.core_item_name_auto = item_name_auto
        self.core_item_name_fr = item_name_fr
        self.core_class_id = classe
        self.core_class_name_auto = class_name_auto
        self.core_class_name_fr = class_name_fr
        self.core_level = level
        self.core_subtitle = subtitle
        self.core_country = country
        self.core_update_timestamp = timestamp
        self.core_usernames = username
        self.core_lat = lat
        self.core_lon = lon
        self.core_osm_ids_elems = elems
        self.core_osm_ids_nodes = None
        self.core_osm_ids_ways = None
        self.core_osm_ids_relations = None
        self.details_descriptionstr = None
        self.details_minlat = None
        self.details_maxlat = None
        self.details_minlon = None
        self.details_maxlon = None
        self.details_b_date_datetime = None
        self.details_osm_json_nodes = None
        self.details_osm_json_ways = None
        self.details_osm_json_relations = None
        self.details_new_elemns = None
        self.osm_objects = None
        self.bduni_zone_collecte_collecteur = None
        self.espaceco_theme = espaceco_theme
        self.bduni_commune_code_insee = None
        self.bduni_commune_nom_officie = None,
        self.bduni_canton_code_insee = None
        self.bduni_arrondissement_code_insee = None
        self.bduni_arrondissement_nom_officiel = None
        self.bduni_collectivite_terr_code_insee = None
        self.bduni_collectivite_terr_nom_officiel = None
        self.bduni_departement_code_insee = None
        self.bduni_departement_nom_officiel = None
        self.bduni_region_code_insee = None
        self.bduni_region_nom_officiel = None
        self.bduni_territoire_nom = None
        self.bduni_territoire_srid = None
        self.bduni_x = None
        self.bduni_y = None
        self.bduni_object_cleabs = None
        self.bduni_objet_attribut_1 = None
        self.bduni_objet_attribut_2 = None
        self.bduni_objet_attribut_3 = None
        self.bduni_objet_attribut_4 = None
        self.bduni_objet_attribut_5 = None
        self.espaceco_signalement_id = None
        self.espaceco_signalement_status = None
        self.espaceco_signalement_status_refresh_timestamp = None
        self.bduni_zicad = None 
        self.cluster_id = None #TODO NEW V1.1
        self.sketchcontent = None #TODO NEW V1.1
        self.core_classe_bduni = core_classe_bduni
        self.bduni_objet_date_modification = None

# def de l'appel avec UUID

    def update_with_uuid(self):
        """Complète l'instance avec les détails Osmose.

        Keyword arguments: self

        Returns:
            Instance osmosecracker_issue.OsmoseCrackerIssue
        """
        if self.core_status == "false":
            jsoncompleentaire = osmosecracker_query_osmose.extracte_osmose_uuid(self.core_id)  # recuperation d'un json avec
            # des données liée a l'objet
            self.details_minlat = jsoncompleentaire["minlat"]
            self.details_maxlat = jsoncompleentaire["maxlat"]
            self.details_minlon = jsoncompleentaire["minlon"]
            self.details_maxlon = jsoncompleentaire["maxlon"]
            self.details_b_date_datetime = datetime.datetime.strptime(
                jsoncompleentaire["date"], '%Y-%m-%dT%H:%M:%S.%f%z')
        else:
            self.details_minlat = None
            self.details_maxlat = None
            self.details_minlon = None
            self.details_maxlon = None
            self.details_b_date_datetime = None

    def markdown_report(self):
        """Complète l'instance avec le texte de rapportage.

        Keyword arguments: self

        Returns:
            Instance osmosecracker_issue.OsmoseCrackerIssue
        """
        name_bot = config.OC_REPORT_KEYWORD
        GAPIParams = [
            ("api", 1),
            ("map_action", "pano"),
            ("viewpoint", f"{self.core_lat},{self.core_lon}")]
        self.details_descriptionstr = (""
                        + name_bot+"\n"
            + " Alerte d'incohérence sur un objet de type"
            + self.core_item_name_fr
            + "\n Incohérence [ "
	        + "** Présence ou Description attributaire **"
            + " ] OSM/IGN."
            + "La cartographie IGN est (Plan IGN J+1) https://www.geoportail.gouv.fr/carte?c={long},{lat}&z=17&l0=GEOGRAPHICALGRIDSYSTEMS.MAPS.BDUNI.J1::GEOPORTAIL:OGC:WMTS(1)&l1=ORTHOIMAGERY.ORTHOPHOTOS::GEOPORTAIL:OGC:WMTS(0.32)&l2=HYDROGRAPHY.BCAE.2025(1)&permalink=yes".format(lat=str(self.core_lat), long=str(self.core_lon))
            )

        if self.bduni_territoire_nom is not None:
            self.details_descriptionstr += self.bduni_territoire_nom + " / "

        if self.bduni_region_nom_officiel is not None:
            self.details_descriptionstr += self.bduni_region_nom_officiel + " / "

        if self.bduni_departement_nom_officiel is not None:
            self.details_descriptionstr += self.bduni_departement_nom_officiel + " / "

        if self.bduni_collectivite_terr_nom_officiel is not None:
            self.details_descriptionstr += self.bduni_collectivite_terr_nom_officiel + " / "

        if self.bduni_commune_nom_officiel is not None:
            self.details_descriptionstr += self.bduni_commune_nom_officiel + " / "

        if self.bduni_arrondissement_nom_officiel is not None:
            self.details_descriptionstr += self.bduni_arrondissement_nom_officiel

        if self.bduni_object_cleabs is not None:
            self.details_descriptionstr += ""
            "\nObjet BDUni concerné:"
            "Cleabs: {bduni_object_cleabs} de date de dernière modification en BDuni {bduni_objet_date}"
            "{attribut_1}: {bduni_objet_attribut_1}"
            "{attribut_2}: {bduni_objet_attribut_2}"
            "{attribut_3}: {bduni_objet_attribut_3}"
            "{attribut_4}: {bduni_objet_attribut_4}"
            "{attribut_5}: {bduni_objet_attribut_5}"
            "\n".format(
                bduni_object_cleabs=self.bduni_object_cleabs,
                attribut_1=config.OC_ITEM_INFO[int(self.core_item_id)]['attributs_bduni']['attribut_1'],
                bduni_objet_attribut_1=self.bduni_objet_attribut_1,
                attribut_2=config.OC_ITEM_INFO[int(self.core_item_id)]['attributs_bduni']['attribut_2'],
                bduni_objet_attribut_2=self.bduni_objet_attribut_2,
                attribut_3=config.OC_ITEM_INFO[int(self.core_item_id)]['attributs_bduni']['attribut_3'],
                bduni_objet_attribut_3=self.bduni_objet_attribut_3,
                attribut_4=config.OC_ITEM_INFO[int(self.core_item_id)]['attributs_bduni']['attribut_4'],
                bduni_objet_attribut_4=self.bduni_objet_attribut_4,
                attribut_5=config.OC_ITEM_INFO[int(self.core_item_id)]['attributs_bduni']['attribut_5'],
                bduni_objet_attribut_5=self.bduni_objet_attribut_5,
                bduni_objet_date=str(self.bduni_objet_date_modification) if self.bduni_objet_date_modification else 'inconnue'
            )

    def bduni_collect_commune(self):
        """Complète l'instance avec les détails BDUni .

        Keyword arguments: self

        Returns:
            Instance osmosecracker_issue.OsmoseCrackerIssue
        """
        LOGGER.debug("bduni_collect")

        self.bduni_zone_collecte_collecteur = (
            osmosecracker_query_bduni.bduni_get_collecteur(
                Latitude=self.core_lat, Longitude=self.core_lon))
        LOGGER.debug("bduni_collect, zone collecteur= {0}".format(self.bduni_zone_collecte_collecteur))

        bduni_commune_dict: dict = osmosecracker_query_bduni.bduni_get_commune(Latitude=self.core_lat, Longitude=self.core_lon)

        self.bduni_commune_code_insee = bduni_commune_dict['bduni_commune_code_insee'] if bduni_commune_dict else None
        self.bduni_commune_nom_officiel = bduni_commune_dict['bduni_commune_nom_officiel'] if bduni_commune_dict else None
        self.bduni_canton_code_insee = bduni_commune_dict['bduni_canton_code_insee'] if bduni_commune_dict else None
        self.bduni_arrondissement_code_insee = bduni_commune_dict['bduni_arrondissement_code_insee'] if bduni_commune_dict else None
        self.bduni_arrondissement_nom_officiel = bduni_commune_dict['bduni_arrondissement_nom_officiel'] if bduni_commune_dict else None
        self.bduni_collectivite_terr_code_insee = bduni_commune_dict['bduni_collectivite_terr_code_insee'] if bduni_commune_dict else None
        self.bduni_collectivite_terr_nom_officiel = bduni_commune_dict['bduni_collectivite_terr_nom_officiel'] if bduni_commune_dict else None
        self.bduni_departement_code_insee = bduni_commune_dict['bduni_departement_code_insee'] if bduni_commune_dict else None
        self.bduni_departement_nom_officiel = bduni_commune_dict['bduni_departement_nom_officiel'] if bduni_commune_dict else None
        self.bduni_region_code_insee = bduni_commune_dict['bduni_region_code_insee'] if bduni_commune_dict else None
        self.bduni_region_nom_officiel = bduni_commune_dict['bduni_region_nom_officiel'] if bduni_commune_dict else None
        LOGGER.debug("bduni_collect commune= {0}".format(str(self.bduni_commune_code_insee)))


    def bduni_collect_complement(self):
        """Complète l'instance avec les détails BDUni.

        Keyword arguments: self

        Returns:
            Instance osmosecracker_issue.OsmoseCrackerIssue
        """
        LOGGER.debug("bduni_collect")
    
        bduni_territoire_dict: dict = osmosecracker_query_bduni.bduni_get_reprojected_point(Latitude=self.core_lat, Longitude=self.core_lon)

        self.bduni_territoire_nom = bduni_territoire_dict['bduni_territoire_nom'] if bduni_territoire_dict else None
        self.bduni_territoire_srid = bduni_territoire_dict['bduni_territoire_srid'] if bduni_territoire_dict else None
        self.bduni_x = bduni_territoire_dict['bduni_x'] if bduni_territoire_dict else None
        self.bduni_y = bduni_territoire_dict['bduni_y'] if bduni_territoire_dict else None
        LOGGER.debug("bduni_collect territoire= {0}".format(str(self.bduni_territoire_nom)))

        bduni_object_dict: dict = osmosecracker_query_bduni.bduni_get_object(Latitude=self.core_lat, Longitude=self.core_lon, Item=int(self.core_item_id))
        LOGGER.debug(bduni_object_dict)
        self.bduni_object_cleabs = bduni_object_dict['bduni_object_cleabs'] if bduni_object_dict else None
        self.bduni_objet_attribut_1 = bduni_object_dict['bduni_objet_attribut_1'] if bduni_object_dict else None
        self.bduni_objet_attribut_2 = bduni_object_dict['bduni_objet_attribut_2'] if bduni_object_dict else None
        self.bduni_objet_attribut_3 = bduni_object_dict['bduni_objet_attribut_3'] if bduni_object_dict else None
        self.bduni_objet_attribut_4 = bduni_object_dict['bduni_objet_attribut_4'] if bduni_object_dict else None
        self.bduni_objet_attribut_5 = bduni_object_dict['bduni_objet_attribut_5'] if bduni_object_dict else None

        self.bduni_objet_date_modification = (bduni_object_dict['bduni_objet_date_modification']).isoformat() if (bduni_object_dict and bduni_object_dict['bduni_objet_date_modification'] != None) else None
        LOGGER.debug("bduni_collect object= {0}".format(str(self.bduni_object_cleabs)))
