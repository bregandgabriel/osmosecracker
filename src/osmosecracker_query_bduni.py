#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# Modif Date v1.1 : July 2024
# version ='1.1'
# ---------------------------------------------------------------------------
""" 
Fonctions de requêtes de la BDUni.

Note
----
Toutes les requêtes sont faites en SQL.
"""
# ---------------------------------------------------------------------------

# Notes
# 
# **codeSQL** 
#
# tuto
# https://pynative.com/python-postgresql-tutorial/

# Imports
from __future__ import annotations  # Utilisé pour postpone all runtime parsing of annotations, https://docs.python.org/3.7/whatsnew/3.7.html#pep-563-postponed-evaluation-of-annotations
import logging
import psycopg2
import psycopg2.extras
import osmosecracker_config
import osmosecracker_exceptions
import json

LOGGER = logging.getLogger('OsmoseCracker.SupQueries.BDUni')


def bduni_get_collecteur(Latitude: float, Longitude: float) -> str:
    """Fonction de récupération de la zone de collecte.

    Keyword arguments:
        Latitude (SRID 4326) du ponctuel Osmose, float.
        Longitude (SRID 4326) du ponctuel Osmose, float.

    Returns:
        None ou le nom du collecteur
    """
    result = None
    LOGGER.debug("bduni_get_collecteur")
    try:
        with psycopg2.connect(
                host=osmosecracker_config.OC_BDUNI_HOST,
                port=osmosecracker_config.OC_BDUNI_PORT,
                dbname=osmosecracker_config.OC_BDUNI_DBNAME,
                user=osmosecracker_config.OC_BDUNI_USER,
                password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:
            sql = """
            **codeSQL**
            """.format(longitude=Longitude, latitude=Latitude)
            # Create a cursor to perform database operations
            cursor = connection.cursor()
            cursor.execute(sql)
            record = cursor.fetchone()
            if record is not None:
                result = record[0]
            else:
                result = "Collecteur inconnu"
                logging.warning("Collecteur inconnu, {0}".format(str(record)))
    except Exception as exc:
        logging.exception(str(exc))
        raise exc
    else:
        return result
    finally:
        LOGGER.debug("bduni_get_collecteur, opération réussie: {0}".format(str(result is not None)))


def bduni_get_reprojected_point(Latitude: float, Longitude: float) -> dict:
    """Fonction de récupération d'Information BDuni
    de la localisation de l'issue

    Keyword arguments:
        Latitude (SRID 4326) du ponctuel Osmose, float.
        Longitude (SRID 4326) du ponctuel Osmose, float.

    Returns: dictionnaire python comprenant
        bduni_territoire_nom, str
        bduni_territoire_code, str
        bduni_territoire_srid, int.
        bduni_x, Longitude reprojetée dans la projection bduni_territoire_srid, float.
        bduni_y, Latitude reprojetée dans la projection bduni_territoire_srid, float.
    """
    result = None
    LOGGER.debug("bduni_get_commune")
    try:
        with psycopg2.connect(
                host=osmosecracker_config.OC_BDUNI_HOST,
                port=osmosecracker_config.OC_BDUNI_PORT,
                dbname=osmosecracker_config.OC_BDUNI_DBNAME,
                user=osmosecracker_config.OC_BDUNI_USER,
                password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:
            sql = """
                    **codeSQL**
            """.format(longitude=Longitude, latitude=Latitude)
            # Create a cursor to perform database operations
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            record = cursor.fetchone()
            if record is not None:
                result = record
            else:
                result = None
                logging.warning("Lat Long invalide, hors territoire français, {0}".format(str(record)))
    except Exception as exc:
        LOGGER.exception(str(exc))
        raise exc
    else:
        return result
    finally:
        LOGGER.debug("bduni_get_commune, opération réussie: {0}".format(str(result is not None)))


def bduni_get_commune(Latitude: float, Longitude: float) -> dict:
    """Fonction de récupération des information sur les commune

    Keyword arguments:
        Latitude (SRID 4326) du ponctuel Osmose, float.
        Longitude (SRID 4326) du ponctuel Osmose, float.

    Returns:
        None ou dictionnaire des information sur la commune
    """
    result = None
    LOGGER.debug("bduni_get_commune")
    try:
        with psycopg2.connect(
                host=osmosecracker_config.OC_BDUNI_HOST,
                port=osmosecracker_config.OC_BDUNI_PORT,
                dbname=osmosecracker_config.OC_BDUNI_DBNAME,
                user=osmosecracker_config.OC_BDUNI_USER,
                password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:
            sql = """
            **codeSQL**
            """.format(longitude=Longitude, latitude=Latitude)
            # Create a cursor to perform database operations
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            record = cursor.fetchone()
            if record is not None: # La commune fait partie d'un département fr
                result = record
            else:
                sql = """
                        **codeSQL**
                        """.format(longitude=Longitude, latitude=Latitude)
                cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cursor.execute(sql)
                record = cursor.fetchone()
                if record is not None: # La commune fait partie d'une collectivité territoriale
                    result = record
                else:
                    result = None
                    logging.warning("Lat Long invalide, hors territoire français, {0}".format(str(record)))
    except Exception as exc:
        LOGGER.exception(str(exc))
        raise exc
    else:
        return result
    finally:
        LOGGER.debug("bduni_get_commune, opération réussie: {0}".format(str(result is not None)))


def bduni_get_object(Latitude: float, Longitude: float, Item: int) -> dict:
    """ Fonction de récupération des information sur l'objet BDuni

    Keyword arguments:
        Latitude (SRID 4326) du ponctuel Osmose, float.
        Longitude (SRID 4326) du ponctuel Osmose, float.

    Returns:
        None ou dictionnaire des information sur l'objet BDuni """
    result = None
    LOGGER.debug("bduni_get_object")
    try:
        with psycopg2.connect(
                host=osmosecracker_config.OC_BDUNI_HOST,
                port=osmosecracker_config.OC_BDUNI_PORT,
                dbname=osmosecracker_config.OC_BDUNI_DBNAME,
                user=osmosecracker_config.OC_BDUNI_USER,
                password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:
            sql = """
            **codeSQL**
            """.format(
                longitude=Longitude,
                latitude=Latitude,
                classe_bdu=osmosecracker_config.OC_ITEM_INFO[Item]['classe_bduni'],
                attribut_bdu_1=osmosecracker_config.OC_ITEM_INFO[Item]['attributs_bduni']['attribut_1'],
                attribut_bdu_2=osmosecracker_config.OC_ITEM_INFO[Item]['attributs_bduni']['attribut_2'],
                attribut_bdu_3=osmosecracker_config.OC_ITEM_INFO[Item]['attributs_bduni']['attribut_3'],
                attribut_bdu_4=osmosecracker_config.OC_ITEM_INFO[Item]['attributs_bduni']['attribut_4'],
                attribut_bdu_5=osmosecracker_config.OC_ITEM_INFO[Item]['attributs_bduni']['attribut_5'],
                attribut_bdu_geom=osmosecracker_config.OC_ITEM_INFO[Item]['attributs_bduni']['attribut_geometrie']
                )
            # Create a cursor to perform database operations
            # gcms_date_modification *********
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            record = cursor.fetchone()
            if record is not None:
                result = record
            else:
                result = None
    except Exception as exc:
        LOGGER.exception(str(exc))
        raise exc
    else:
        return result
    finally:
        LOGGER.debug("bduni_get_object, opération réussie: {0}".format(str(result is not None)))


def bduni_get_list_dep() -> [str]:
    """Fonction de récupération de la liste des départements au sens service de l'état

    Keyword arguments:

    Returns:
        Liste de str des codes insee des départements au sens service de l'état
    """
    result:[str] = []
    LOGGER.debug("bduni_get_list_dep")
    try:
        with psycopg2.connect(
                host=osmosecracker_config.OC_BDUNI_HOST,
                port=osmosecracker_config.OC_BDUNI_PORT,
                dbname=osmosecracker_config.OC_BDUNI_DBNAME,
                user=osmosecracker_config.OC_BDUNI_USER,
                password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:
            sql = """
            **codeSQL**
            """
            # Create a cursor to perform database operations
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            record = cursor.fetchall()
            if record is not None:
                for index, element in enumerate(record):
                    result.append(element['code_insee'])
                result.append("977") #*********
                result.append("978")
            else:
                
                result = []
    except Exception as exc:
        LOGGER.exception(str(exc))
        raise exc
    else:
        return result
    finally:
        LOGGER.debug("bduni_get_list_dep, opération réussie: {0}".format(str(result is not None)))


def bduni_get_list_reg() -> [str]:
    """Fonction de récupération de la liste des régions BDUni

    Keyword arguments:

    Returns:
        Liste de str des codes insee des régions BDUni
    """
    result:[str] = []
    LOGGER.debug("bduni_get_list_dep")
    try:
        with psycopg2.connect(
                host=osmosecracker_config.OC_BDUNI_HOST,
                port=osmosecracker_config.OC_BDUNI_PORT,
                dbname=osmosecracker_config.OC_BDUNI_DBNAME,
                user=osmosecracker_config.OC_BDUNI_USER,
                password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:
            sql = """
            **codeSQL**
            """
            # Create a cursor to perform database operations
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            record = cursor.fetchall()
            if record is not None:
                for index, element in enumerate(record):
                    result.append(element['code_insee'])
            else:
                result = []
    except Exception as exc:
        LOGGER.exception(str(exc))
        raise exc
    else:
        return result
    finally:
        LOGGER.debug("bduni_get_list_dep, opération réussie: {0}".format(str(result is not None)))


def is_in_zicad(issuesSignalement: List[osmosecracker_issue.OsmoseCrackerIssue]) -> [osmosecracker_issue.OsmoseCrackerIssue]:
    """Fonction de récupération des information sur les zicad
    pour connaitre si l'issue est dans une zicad

    Keyword arguments:
        osmosecrackerIssue,
        objet de la classe osmosecracker_issue.OsmoseCrackerIssue.

    Returns:
        Instance d'osmosecracker_issue.OsmoseCrackerIssue modifiée.
    """
    loopIssueList: List[osmosecracker_issue.OsmoseCrackerIssue] = issuesSignalement
    updatedIssueList: List[osmosecracker_issue.OsmoseCrackerIssue] = list()
    try:
        with psycopg2.connect(
        host=osmosecracker_config.OC_BDUNI_HOST,
        port=osmosecracker_config.OC_BDUNI_PORT,
        dbname=osmosecracker_config.OC_BDUNI_DBNAME,
        user=osmosecracker_config.OC_BDUNI_USER,
        password=osmosecracker_config.OC_BDUNI_PASSWORD) as connection:

            # Create the temporary table once outside of the loop
            # On reprojette la table des territoires en 4326
            sql = """
            **codeSQL**
            """
            cursor = connection.cursor()
            cursor.execute(sql)

            LOGGER.debug('osmosecracker_query_bduni.is_in_zicad, Create Temporary table zicad_table OK')

            # Iterate through resultats
            for index, element in enumerate(loopIssueList):
                LOGGER.debug('Recherche des infos sur l issue {0} de long={1} et lat = {2}'.format(loopIssueList[index].core_id, loopIssueList[index].core_lon, loopIssueList[index].core_lat))
                # Create and execute the second query
                second_query = """**codeSQL**""".format(long=loopIssueList[index].core_lon, lat=loopIssueList[index].core_lat)
                cursor.execute(second_query)
                results = cursor.fetchall()
                if not results[0][0] is None:
                    loopIssueList[index].bduni_zicad = results[0][0]
                    updatedIssueList.append(loopIssueList[index])
                LOGGER.debug('Recherche des infos sur l issue {0} de long={1} et lat = {2}, résultat={3}'.format(loopIssueList[index].core_id, loopIssueList[index].core_lon, loopIssueList[index].core_lat, loopIssueList[index].bduni_zicad))

            # Close the cursor and connection after processing all rows in resultats
            cursor.close()
            LOGGER.debug('Recherche des intersection zicad n={0} issue traitées'.format(len(updatedIssueList)))

    except Exception as exc:
        LOGGER.error("Erreur lors de la requête zicad \n" + exc)
        raise exc
    finally:
        return(updatedIssueList)

#TODO NEW V1.1  
def clustering(issues: List[osmosecracker_issue.OsmoseCrackerIssue])-> List[osmosecracker_issue.OsmoseCrackerIssue]:
    LOGGER.debug("clustering:")
    LOGGER.debug(issues)
    """
    PRETRAITEMENT issues to JSON
    """ 
    json_issues = json.dumps([{
    "core_id": issue.core_id,
    "core_lat": issue.core_lat,
    "core_lon": issue.core_lon,
    "core_item_id": issue.core_item_id,
    "core_class_id": issue.core_class_id,
    "bduni_objet_attribut_1": issue.bduni_objet_attribut_1
    } for issue  in issues], indent=4)
    LOGGER.debug(json_issues)
    LOGGER.debug("debut clustering")
    """
    TRAITEMENT clusterisation avec ST_ClusterDBSCAN

    Pour la distance max entre 2 point j'ai pris 1km
    en inclinésont celon le centre de la france 
    (46° 32′ 23″ N, 2° 25′ 49″ E) https://fr.wikipedia.org/wiki/Centre_de_la_France
    """
    LOGGER.debug("debut requete SQL clustering")
    try:
        with psycopg2.connect(
        host=osmosecracker_config.OC_BDUNI_HOST,
        port=osmosecracker_config.OC_BDUNI_PORT,
        dbname=osmosecracker_config.OC_BDUNI_DBNAME,
        user=osmosecracker_config.OC_BDUNI_USER,
        password=osmosecracker_config.OC_BDUNI_PASSWORD
        ) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                clustering_sql = """
                **codeSQL**
                """
                cur.execute(clustering_sql, (json_issues,))
                clustered_rows = cur.fetchall()
        connection.commit()
    except Exception as exc:
        LOGGER.exception(str(exc))
        raise exc
    LOGGER.debug("fin requete SQL clustering")

    LOGGER.debug("début corresponddance objet de classe issues avec ligne retourner par la requete SQL")
    order_issues: list(osmosecracker_issue.OsmoseCrackerIssue) = []
    if clustered_rows is not None:          
        # pour chaque ligne retournée
        for row in clustered_rows:
            # on cherche l'objet de classe issues correspondant avec 'core_id'
            for issue in issues:
                if (issue.core_id == row['core_id']):
                    # Traitement differentier si cluster existe
                    if row['cluster_id'] != None:
                        LOGGER.debug("New Cluster Creat")

                        issue.cluster_id = row['cluster_id']

                        bounding_box = str(row["bounding_box"])
                        bounding_center_lat = str(row["bounding_center_lat"])
                        bounding_center_lon = str(row["bounding_center_lon"])
                        sketchcontent = sketchcontent = {
                            "desc": "Emprise du cluster",
                            "name": "Emprise du cluster",
                            "objects": [{
                                "type": "Polygone",
                                "geometry": bounding_box,
                                "attributes": {}
                            }],
                            "contexte": {
                                "lat": bounding_center_lat,
                                "lon": bounding_center_lon,
                                "zoom": "17"
                            }
                        }
                        issue.sketchcontent = sketchcontent
                    else:
                        issue.cluster_id = None
                        issue.sketchcontent = None
                    order_issues.append(issue) 
    LOGGER.debug("fin clustering")
    return(order_issues)
