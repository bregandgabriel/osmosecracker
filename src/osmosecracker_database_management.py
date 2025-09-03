#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# version ='1.1'
# ---------------------------------------------------------------------------
""" 
Classe singleton responsable de la persistance sqlite
des informations Osmose.

Parameters
----------
object : 'class'
    La structure de la classe est identique à celle 
    créée dans osmosecracker_issue.

Returns
-------
osmosecracker_database.sqlite : 'sqlit'
    Les nouvelles données sont ajoutées, 
    et les statuts Espace Collaboratif sont actualisés.

Usage
-----
from osmosecracker_database_management import osmosecrackerDatabase
osmosecrackerDatabase.exists()

Note
----
Si de nouvelles données doivent être ajoutées
à la base de données, ce fichier, le fichier SQLite et
le fichier osmosecracker_issue doivent être modifiés.
"""
# ---------------------------------------------------------------------------

# Notes
# https://docs.python.org/3/library/sqlite3.html#sqlite3-connection-context-manager
# Singleton via module, cf. https://stackoverflow.com/a/52930277

# Imports
import datetime
import logging
import os
import pathlib
import sqlite3
from typing import Final, final, ClassVar
import uuid
import osmosecracker_exceptions
import osmosecracker_issue
import osmosecracker_config

LOGGER = logging.getLogger('OsmoseCracker.DatabaseManagement')


class _osmosecrackerDatabase(object):
    """Une classe responsable de la persistance sqlite des informations."""

    databaseDirectoryPath: pathlib.PurePath
    "Chemin d'accès à la base de données"

    def __init__(self):
        """Crée et initialise l'instance de osmosecrackerDatabase.

        Keyword arguments: None

        Returns:
            Instance (singleton) de osmosecrackerDatabase
        """
        self.databaseFilePath = pathlib.Path(
            __file__).resolve().parent.joinpath(
            'osmosecracker_database.sqlite')
        LOGGER.info("""Instanciation du singleton d'accès à
        la base de données locale SQLite""")

    def exists(self) -> bool:
        """Vérifie que le fichier de la base SQLite existe.

        Keyword arguments: None

        Returns:
            Boolean déterminant l'existance du fichier de la base SQLite.
        """
        SQLiteDBExists = self.databaseFilePath.exists()
        LOGGER.debug("La base de données SQLite {0} existe: {1}".format(
            str(self.databaseFilePath),
            str(SQLiteDBExists)))
        return SQLiteDBExists

    def is_available(self) -> bool:
        """Vérifie que le fichier de la base SQLite existe,
        et est une base SQLite à laquelle on peut se connecter.

        Keyword arguments: None

        Returns:
            Boolean déterminant que le fichier de la base SQLite existe et
            est une base SQLite à laquelle on peut se connecter.
        """
        SQLiteDBAvailable = False
        try:
            if self.exists():
                con = sqlite3.connect(
                    "file:{0}?mode=rw".format(str(self.databaseFilePath)),
                    uri=True)
                con.close()
                SQLiteDBAvailable = True
        except Exception as exc:
            LOGGER.exception(
                "Erreur à la vérification de la disponibilité"
                " de la base de données SQLite, {0}".format(str(exc)))
            raise exc
        else:
            return SQLiteDBAvailable
        finally:
            LOGGER.debug(
                "La base de données SQLite {0} "
                "existe+disponible: {1}".format(
                              str(self.databaseFilePath),
                              str(SQLiteDBAvailable)))

    def is_valid(self) -> bool:
        """Vérifie que le fichier de la base SQLite existe,
        et est une base SQLite à laquelle on peut se connecter,
        et possède une structure valide.

        Keyword arguments: None

        Returns:
            Boolean déterminant que le fichier de la base SQLite existe et
            est une base SQLite à laquelle on peut se connecter et
            possède une structure valide.
        """
        SQLiteDBValid = False
        try:
            if self.is_available():
                with sqlite3.connect(
                        str(self.databaseFilePath)) as sqlite3connection:

                    # set de tuples (<nom table>,<nom colonne>,<type colonne>)
                    set_structure = set([
                        ("osmoseissue", "core_id", "varchar(50)"),
                        ("osmoseissue", "core_status", "varchar(10)"),
                        ("osmoseissue", "core_lat", "float"),
                        ("osmoseissue", "core_lon", "float"),
                        ("osmoseissue", "core_item_id", "varchar(10)"),
                        ("osmoseissue", "core_item_name_auto", "text"),
                        ("osmoseissue", "core_item_name_fr", "text"),
                        ("osmoseissue", "core_source", "int"),
                        ("osmoseissue", "core_class_id", "int"),
                        ("osmoseissue", "core_class_name_auto", "text"),
                        ("osmoseissue", "core_class_name_fr", "text"),
                        ("osmoseissue", "core_subtitle", "text"),
                        ("osmoseissue", "core_country", "text"),
                        ("osmoseissue", "core_level", "int"),
                        ("osmoseissue", "core_update_timestamp", "text"),
                        ("osmoseissue", "core_osm_ids_elems", "text"),
                        ("osmoseissue", "core_usernames", "text"),
                        ("osmoseissue", "core_osm_ids_nodes", "text"),
                        ("osmoseissue", "core_osm_ids_ways", "text"),
                        ("osmoseissue", "core_osm_ids_relations", "text"),
                        ("osmoseissue", "details_descriptionstr", "text"),
                        ("osmoseissue", "details_minlat", "float"),
                        ("osmoseissue", "details_maxlat", "float"),
                        ("osmoseissue", "details_minlon", "float"),
                        ("osmoseissue", "details_maxlon", "float"),
                        ("osmoseissue", "details_b_date_datetime", "text"),
                        ("osmoseissue", "details_osm_json_nodes", "text"),
                        ("osmoseissue", "details_osm_json_ways", "text"),
                        ("osmoseissue", "details_osm_json_relations", "text"),
                        ("osmoseissue", "details_new_elemns", "text"),
                        ("osmoseissue", "osm_objects", "text"),
                        ("osmoseissue", "bduni_zone_collecte_collecteur", "text"),
                        ("osmoseissue", "espaceco_theme", "text"),
                        ("osmoseissue", "bduni_commune_code_insee", "varchar(5)"),
                        ("osmoseissue", "bduni_commune_nom_officiel", "varchar(80)"),
                        ("osmoseissue", "bduni_canton_code_insee", "varchar(5)"),
                        ("osmoseissue", "bduni_arrondissement_code_insee", "varchar(5)"),
                        ("osmoseissue", "bduni_arrondissement_nom_officiel", "text"),
                        ("osmoseissue", "bduni_collectivite_terr_code_insee", "varchar(5)"),
                        ("osmoseissue", "bduni_collectivite_terr_nom_officiel", "text"),
                        ("osmoseissue", "bduni_departement_code_insee", "varchar(5)"),
                        ("osmoseissue", "bduni_departement_nom_officiel", "text"),
                        ("osmoseissue", "bduni_region_code_insee", "varchar(5)"),
                        ("osmoseissue", "bduni_region_nom_officiel", "text"),
                        ("osmoseissue", "bduni_territoire_nom", "text"),
                        ("osmoseissue", "bduni_territoire_srid", "int"),
                        ("osmoseissue", "bduni_x", "float"),
                        ("osmoseissue", "bduni_y", "float"),
                        ("osmoseissue", "bduni_object_cleabs", "text"),
                        ("osmoseissue", "bduni_objet_attribut_1", "text"),
                        ("osmoseissue", "bduni_objet_attribut_2", "text"),
                        ("osmoseissue", "bduni_objet_attribut_3", "text"),
                        ("osmoseissue", "bduni_objet_attribut_4", "text"),
                        ("osmoseissue", "bduni_objet_attribut_5", "text"),
                        ("osmoseissue", "espaceco_signalement_id", "int"),
                        ("osmoseissue", "espaceco_signalement_status", "text"),
                        ("osmoseissue", "espaceco_signalement_status_refresh_timestamp", "text"),
                        ("osmoseissue", "bduni_objet_zicad", "boolean"),
                        ("osmoseissue", "core_classe_bduni", "text"),
                        ("osmoseissue", "bduni_objet_date_modification", "text"),
                        ("workflowexecutions", "dbid", "integer"),
                        ("workflowexecutions", "workflow_guuid", "varchar(50)"),
                        ("workflowexecutions", "workflow_parameters", "text"),
                        ("workflowexecutions", "timestamp_workflow_start", "text"),
                        ("workflowexecutions", "timestamp_issues_collecting_start", "text"),
                        ("workflowexecutions", "timestamp_issues_collecting_end", "text"),
                        ("workflowexecutions", "timestamp_details_uuid_added", "text"),
                        ("workflowexecutions", "timestamp_workflow_end", "text"),
                        ("workflowexecutions", "workflow_exception_log", "text"),
                        ("workflowexecutions", "stats_issues_collected_count", "int"),
                        ("workflowexecutions", "stats_issues_collected_new_count", "int"),
                        ("workflowexecutions", "stats_issues_reported_count", "int")
                    ])

                    # Requête du meta modèle SQLite
                    sql = """
                    WITH pragma AS (
                        SELECT *, 'osmoseissue' as tablename FROM pragma_table_info('osmoseissue')
                        UNION ALL
                        SELECT *, 'workflowexecutions' as tablename FROM pragma_table_info('workflowexecutions')
                        )
                        SELECT
                        LOWER(tablename), LOWER(name), LOWER(type)
                        FROM pragma;
                    """
                    cur = sqlite3connection.cursor()
                    cur.execute(sql)
                    result = cur.fetchall()
                    set_db = set(result)

                    # Magic function, symmetric difference sur des sets
                    # casse minuscule
                    # LOGGER.debug("Théorie\n" + str(set_structure) + "\n")
                    # LOGGER.debug("Pratique\n" + str(set_db) + "\n")
                    dif = set_structure.symmetric_difference(set_db)
                    LOGGER.debug("Différence\n" + str(dif) + "\n")

                    # Si ensemble vide, alors tous (et uniquements ceux là)
                    # les attributs sont présents
                    if len(dif) == 0:
                        SQLiteDBValid = True
        except Exception as exc:
            LOGGER.exception(
                "Erreur à la vérification de la validité"
                " de la base de données SQLite, {0}".format(str(exc)))
            raise exc
        else:
            return SQLiteDBValid
        finally:
            LOGGER.debug(
                "La base de données SQLite {0} "
                "existe+disponible+conforme: {1}".format(
                    str(self.databaseFilePath), str(SQLiteDBValid)))

    def create(self) -> bool:
        """Crée la base de donnée SQLite si le fichier n'existe pas.

        Keyword arguments: None

        Returns:
            Boolean déterminant la bonne exécution de
            la création de la base SQLite.
        """
        result = False
        if not self.exists():
            LOGGER.info("Création de la base de données SQLite {0}".format(
                str(self.databaseFilePath)))
            try:
                with sqlite3.connect(
                        str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    sql = """
                        CREATE TABLE osmoseissue(
                        core_id VARCHAR(50) UNIQUE NOT NULL,
                        core_status VARCHAR(10) NOT NULL,
                        core_lat FLOAT NOT NULL,
                        core_lon FLOAT NOT NULL,
                        core_item_id VARCHAR(10) NOT NULL,
                        core_item_name_auto TEXT,
                        core_item_name_fr TEXT,
                        core_source INT NOT NULL,
                        core_class_id INT NOT NULL,
                        core_class_name_auto TEXT,
                        core_class_name_fr TEXT,
                        core_subtitle TEXT,
                        core_country TEXT,
                        core_level INT,
                        core_update_timestamp TEXT NOT NULL,
                        core_usernames TEXT,
                        core_osm_ids_elems TEXT,
                        core_osm_ids_nodes TEXT,
                        core_osm_ids_ways TEXT,
                        core_osm_ids_relations TEXT,
                        details_descriptionstr TEXT,
                        details_minlat FLOAT,
                        details_maxlat FLOAT,
                        details_minlon FLOAT,
                        details_maxlon FLOAT,
                        details_b_date_datetime TEXT,
                        details_osm_json_nodes TEXT,
                        details_osm_json_ways TEXT,
                        details_osm_json_relations TEXT,
                        details_new_elemns TEXT,
                        osm_objects TEXT,
                        bduni_zone_collecte_collecteur TEXT,
                        espaceco_theme TEXT,
                        bduni_commune_code_insee VARCHAR(5),
                        bduni_commune_nom_officiel VARCHAR(80),
                        bduni_canton_code_insee VARCHAR(5),
                        bduni_arrondissement_code_insee VARCHAR(5),
                        bduni_arrondissement_nom_officiel TEXT,
                        bduni_collectivite_terr_code_insee VARCHAR(5),
                        bduni_collectivite_terr_nom_officiel TEXT,
                        bduni_departement_code_insee VARCHAR(5),
                        bduni_departement_nom_officiel TEXT,
                        bduni_region_code_insee VARCHAR(5),
                        bduni_region_nom_officiel TEXT,
                        bduni_territoire_nom TEXT,
                        bduni_territoire_srid INT,
                        bduni_x FLOAT,
                        bduni_y FLOAT,
                        bduni_object_cleabs TEXT,
                        bduni_objet_attribut_1 TEXT,
                        bduni_objet_attribut_2 TEXT,
                        bduni_objet_attribut_3 TEXT,
                        bduni_objet_attribut_4 TEXT,
                        bduni_objet_attribut_5 TEXT,
                        espaceco_signalement_id INT,
                        espaceco_signalement_status TEXT,
                        espaceco_signalement_status_refresh_timestamp TEXT,
                        bduni_objet_zicad BOOLEAN,
                        core_classe_bduni TEXT,
                        bduni_objet_date_modification TEXT
                        );
                    """
                    LOGGER.debug(sql)
                    cur = sqlite3connection.cursor()
                    cur.execute(sql)
                    sqlite3connection.commit()
                    sql = """
                        CREATE TABLE workflowexecutions(
                            dbid INTEGER PRIMARY KEY AUTOINCREMENT,
                            workflow_guuid VARCHAR(50) UNIQUE NOT NULL,
                            workflow_parameters TEXT,
                            timestamp_workflow_start TEXT NOT NULL,
                            timestamp_issues_collecting_start TEXT,
                            timestamp_issues_collecting_end TEXT,
                            timestamp_details_uuid_added TEXT,
                            timestamp_workflow_end TEXT,
                            workflow_exception_log TEXT,
                            stats_issues_collected_count INT,
                            stats_issues_collected_new_count INT,
                            stats_issues_reported_count INT

                        );
                    """
                    LOGGER.debug(sql)
                    cur.execute(sql)
                    sqlite3connection.commit()
                    sql = """
                        CREATE INDEX espacecoids_index
                        on osmoseissue (espaceco_signalement_id ASC);
                    """
                    cur.execute(sql)
                    sqlite3connection.commit()
                    sql = """
                        CREATE INDEX espacecostatuses_index
                        on osmoseissue (espaceco_signalement_status ASC);
                    """
                    cur.execute(sql)
                    sqlite3connection.commit()
                    sql = """
                        CREATE INDEX espaceco_signalement_status_refresh_timestamp_index
                        on osmoseissue (espaceco_signalement_status_refresh_timestamp ASC);
                    """
                    cur.execute(sql)

                    result = True

            except Exception as exc:
                LOGGER.exception(
                    "Erreur à la création"
                    " de la base de données SQLite, {0}".format(str(exc)))
                raise exc
            else:
                return result
            finally:
                LOGGER.info(
                    "Création de la base de données"
                    " SQLite {0}, opération réussie: {1}".format(
                        str(self.databaseFilePath),
                        str(result is not None)))
        else:
            raise FileExistsError(str(self.databaseFilePath))

    def insert(self,
               osmosecrackerIssue: osmosecracker_issue.OsmoseCrackerIssue) -> int:
        """Fonction d'insertion de l'objet Osmose, complet.

        Keyword arguments:
            osmosecrackerIssue, objet de la classe
            osmosecracker_issue.OsmoseCrackerIssue,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'insertion.
        """
        result = None
        LOGGER.debug("Insertion/sauvegarde de l'objet Osmose")
        try:
            if self.is_valid():
                with sqlite3.connect(
                        str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        INSERT INTO osmoseissue(
                        core_id,
                        core_status,
                        core_lat,
                        core_lon,
                        core_item_id,
                        core_item_name_auto,
                        core_item_name_fr,
                        core_source,
                        core_class_id,
                        core_class_name_auto,
                        core_class_name_fr,
                        core_subtitle,
                        core_country,
                        core_level,
                        core_update_timestamp,
                        core_usernames,
                        core_osm_ids_elems,
                        core_osm_ids_nodes,
                        core_osm_ids_ways,
                        core_osm_ids_relations,
                        details_descriptionstr,
                        details_minlat,
                        details_maxlat,
                        details_minlon,
                        details_maxlon,
                        details_b_date_datetime,
                        details_osm_json_nodes,
                        details_osm_json_ways,
                        details_osm_json_relations,
                        details_new_elemns,
                        osm_objects,
                        bduni_zone_collecte_collecteur,
                        espaceco_theme,
                        bduni_commune_code_insee,
                        bduni_commune_nom_officiel,
                        bduni_canton_code_insee,
                        bduni_arrondissement_code_insee,
                        bduni_arrondissement_nom_officiel,
                        bduni_collectivite_terr_code_insee,
                        bduni_collectivite_terr_nom_officiel,
                        bduni_departement_code_insee,
                        bduni_departement_nom_officiel,
                        bduni_region_code_insee,
                        bduni_region_nom_officiel,
                        bduni_territoire_nom,
                        bduni_territoire_srid,
                        bduni_x,
                        bduni_y,
                        bduni_object_cleabs,
                        bduni_objet_attribut_1,
                        bduni_objet_attribut_2,
                        bduni_objet_attribut_3,
                        bduni_objet_attribut_4,
                        bduni_objet_attribut_5,
                        espaceco_signalement_id,
                        espaceco_signalement_status,
                        espaceco_signalement_status_refresh_timestamp,
                        bduni_objet_zicad,
                        core_classe_bduni,
                        bduni_objet_date_modification
                        ) VALUES
                        (
                        {core_id},
                        {core_status},
                        {core_lat},
                        {core_lon},
                        {core_item_id},
                        {core_item_name_auto},
                        {core_item_name_fr},
                        {core_source},
                        {core_class_id},
                        {core_class_name_auto},
                        {core_class_name_fr},
                        {core_subtitle},
                        {core_country},
                        {core_level},
                        {core_update_timestamp},
                        {core_usernames},
                        {core_osm_ids_elems},
                        {core_osm_ids_nodes},
                        {core_osm_ids_ways},
                        {core_osm_ids_relations},
                        {details_descriptionstr},
                        {details_minlat},
                        {details_maxlat},
                        {details_minlon},
                        {details_maxlon},
                        {details_b_date_datetime},
                        {details_osm_json_nodes},
                        {details_osm_json_ways},
                        {details_osm_json_relations},
                        {details_new_elemns},
                        {osm_objects},
                        {bduni_zone_collecte_collecteur},
                        {espaceco_theme},
                        {bduni_commune_code_insee},
                        {bduni_commune_nom_officiel},
                        {bduni_canton_code_insee},
                        {bduni_arrondissement_code_insee},
                        {bduni_arrondissement_nom_officiel},
                        {bduni_collectivite_terr_code_insee},
                        {bduni_collectivite_terr_nom_officiel},
                        {bduni_departement_code_insee},
                        {bduni_departement_nom_officiel},
                        {bduni_region_code_insee},
                        {bduni_region_nom_officiel},
                        {bduni_territoire_nom},
                        {bduni_territoire_srid},
                        {bduni_x},
                        {bduni_y},
                        {bduni_object_cleabs},
                        {bduni_objet_attribut_1},
                        {bduni_objet_attribut_2},
                        {bduni_objet_attribut_3},
                        {bduni_objet_attribut_4},
                        {bduni_objet_attribut_5},
                        {espaceco_signalement_id},
                        {espaceco_signalement_status},
                        {espaceco_signalement_status_refresh_timestamp},
                        {bduni_objet_zicad},
                        {core_classe_bduni},
                        {bduni_objet_date_modification}
                        ) RETURNING rowid;
                    """.format(
                        core_id=("'"+osmosecrackerIssue.core_id+"'"),
                        core_status=("'"+osmosecrackerIssue.core_status+"'"),
                        core_lat=osmosecrackerIssue.core_lat,
                        core_lon=osmosecrackerIssue.core_lon,
                        core_item_id=osmosecrackerIssue.core_item_id,
                        core_item_name_auto=("'"+osmosecrackerIssue.core_item_name_auto.replace("'", "''")+"'") if osmosecrackerIssue.core_item_name_auto else 'NULL',
                        core_item_name_fr=("'"+osmosecrackerIssue.core_item_name_fr.replace("'", "''")+"'") if osmosecrackerIssue.core_item_name_fr else 'NULL',
                        core_source=osmosecrackerIssue.core_source,
                        core_class_id=osmosecrackerIssue.core_class_id,
                        core_class_name_auto=("'"+osmosecrackerIssue.core_class_name_auto.replace("'", "''")+"'") if osmosecrackerIssue.core_class_name_auto else 'NULL',
                        core_class_name_fr=("'"+osmosecrackerIssue.core_class_name_fr.replace("'", "''")+"'") if osmosecrackerIssue.core_class_name_fr else 'NULL',
                        core_subtitle=("'"+osmosecrackerIssue.core_subtitle.replace("'", "''")+"'") if osmosecrackerIssue.core_subtitle else 'NULL',
                        core_country=("'"+osmosecrackerIssue.core_country+"'") if osmosecrackerIssue.core_country else 'NULL',
                        core_level=osmosecrackerIssue.core_level,
                        core_update_timestamp=("'"+osmosecrackerIssue.core_update_timestamp.isoformat()+"'") if osmosecrackerIssue.core_update_timestamp else 'NULL',
                        core_usernames=("'"+osmosecrackerIssue.core_usernames+"'") if osmosecrackerIssue.core_usernames else 'NULL',
                        core_osm_ids_elems=("'"+','.join(str(osmosecrackerIssue.core_osm_ids_elems))+"'") if osmosecrackerIssue.core_osm_ids_elems else 'NULL',
                        core_osm_ids_nodes=("'"+','.join(str(osmosecrackerIssue.core_osm_ids_nodes))+"'") if osmosecrackerIssue.core_osm_ids_nodes else 'NULL',
                        core_osm_ids_ways=("'"+','.join(str(osmosecrackerIssue.core_osm_ids_ways))+"'") if osmosecrackerIssue.core_osm_ids_ways else 'NULL',
                        core_osm_ids_relations=("'"+','.join(str(osmosecrackerIssue.core_osm_ids_relations))+"'") if osmosecrackerIssue.core_osm_ids_relations else 'NULL',
                        details_descriptionstr=("'"+osmosecrackerIssue.details_descriptionstr.replace("'", "''")+"'") if osmosecrackerIssue.details_descriptionstr else 'NULL',
                        details_minlat=osmosecrackerIssue.details_minlat if osmosecrackerIssue.details_minlat else 'NULL',
                        details_maxlat=osmosecrackerIssue.details_maxlat if osmosecrackerIssue.details_maxlat else 'NULL',
                        details_minlon=osmosecrackerIssue.details_minlon if osmosecrackerIssue.details_minlon else 'NULL',
                        details_maxlon=osmosecrackerIssue.details_maxlon if osmosecrackerIssue.details_maxlon else 'NULL',
                        details_b_date_datetime=("'"+osmosecrackerIssue.details_b_date_datetime.isoformat()+"'") if osmosecrackerIssue.details_b_date_datetime else 'NULL',
                        details_osm_json_nodes=("'"+osmosecrackerIssue.details_osm_json_nodes+"'") if osmosecrackerIssue.details_osm_json_nodes else 'NULL',
                        details_osm_json_ways=("'"+osmosecrackerIssue.details_osm_json_ways+"'") if osmosecrackerIssue.details_osm_json_ways else 'NULL',
                        details_osm_json_relations=("'"+osmosecrackerIssue.details_osm_json_relations+"'") if osmosecrackerIssue.details_osm_json_relations else 'NULL',
                        details_new_elemns=("'"+osmosecrackerIssue.details_new_elemns+"'") if osmosecrackerIssue.details_new_elemns else 'NULL',
                        osm_objects=("'"+osmosecrackerIssue.osm_objects+"'") if osmosecrackerIssue.osm_objects else 'NULL',
                        bduni_zone_collecte_collecteur=("'"+osmosecrackerIssue.bduni_zone_collecte_collecteur+"'") if osmosecrackerIssue.bduni_zone_collecte_collecteur else 'NULL',
                        espaceco_theme=("'" + osmosecrackerIssue.espaceco_theme + "'") if osmosecrackerIssue.espaceco_theme else 'NULL',
                        bduni_commune_code_insee=("'" + osmosecrackerIssue.bduni_commune_code_insee + "'") if osmosecrackerIssue.bduni_commune_code_insee else 'NULL',
                        bduni_commune_nom_officiel=("'" + osmosecrackerIssue.bduni_commune_nom_officiel.replace("'", "''") + "'") if osmosecrackerIssue.bduni_commune_nom_officiel else 'NULL',
                        bduni_canton_code_insee=("'" + osmosecrackerIssue.bduni_canton_code_insee + "'") if osmosecrackerIssue.bduni_canton_code_insee else 'NULL',
                        bduni_arrondissement_code_insee=("'" + osmosecrackerIssue.bduni_arrondissement_code_insee + "'") if osmosecrackerIssue.bduni_arrondissement_code_insee else 'NULL',
                        bduni_arrondissement_nom_officiel=("'" + osmosecrackerIssue.bduni_arrondissement_nom_officiel.replace("'", "''") + "'") if osmosecrackerIssue.bduni_arrondissement_nom_officiel else 'NULL',
                        bduni_collectivite_terr_code_insee=("'" + osmosecrackerIssue.bduni_collectivite_terr_code_insee + "'") if osmosecrackerIssue.bduni_collectivite_terr_code_insee else 'NULL',
                        bduni_collectivite_terr_nom_officiel=("'" + osmosecrackerIssue.bduni_collectivite_terr_nom_officiel.replace("'", "''") + "'") if osmosecrackerIssue.bduni_collectivite_terr_nom_officiel else 'NULL',
                        bduni_departement_code_insee=("'" + osmosecrackerIssue.bduni_departement_code_insee + "'") if osmosecrackerIssue.bduni_departement_code_insee else 'NULL',
                        bduni_departement_nom_officiel=("'" + osmosecrackerIssue.bduni_departement_nom_officiel.replace("'", "''") + "'") if osmosecrackerIssue.bduni_departement_nom_officiel else 'NULL',
                        bduni_region_code_insee=("'" + osmosecrackerIssue.bduni_region_code_insee + "'") if osmosecrackerIssue.bduni_region_code_insee else 'NULL',
                        bduni_region_nom_officiel=("'" + osmosecrackerIssue.bduni_region_nom_officiel.replace("'", "''") + "'") if osmosecrackerIssue.bduni_region_nom_officiel else 'NULL',
                        bduni_territoire_nom=("'" + osmosecrackerIssue.bduni_territoire_nom.replace("'", "''") + "'") if osmosecrackerIssue.bduni_territoire_nom else 'NULL',
                        bduni_territoire_srid=osmosecrackerIssue.bduni_territoire_srid if osmosecrackerIssue.bduni_territoire_srid else 'NULL',
                        bduni_x=osmosecrackerIssue.bduni_x if osmosecrackerIssue.bduni_x else 'NULL',
                        bduni_y=osmosecrackerIssue.bduni_y if osmosecrackerIssue.bduni_y else 'NULL',
                        bduni_object_cleabs=("'" + osmosecrackerIssue.bduni_object_cleabs.replace("'", "''") + "'") if osmosecrackerIssue.bduni_object_cleabs else 'NULL',
                        bduni_objet_attribut_1=("'" + osmosecrackerIssue.bduni_objet_attribut_1.replace("'", "''") + "'") if osmosecrackerIssue.bduni_objet_attribut_1 else 'NULL',
                        bduni_objet_attribut_2=("'" + osmosecrackerIssue.bduni_objet_attribut_2.replace("'", "''") + "'") if osmosecrackerIssue.bduni_objet_attribut_2 else 'NULL',
                        bduni_objet_attribut_3="'" + (osmosecrackerIssue.bduni_objet_attribut_3.replace("'", "''") + "'") if osmosecrackerIssue.bduni_objet_attribut_3 else 'NULL',
                        bduni_objet_attribut_4=("'" + osmosecrackerIssue.bduni_objet_attribut_4.replace("'", "''") + "'") if osmosecrackerIssue.bduni_objet_attribut_4 else 'NULL',
                        bduni_objet_attribut_5=("'" + osmosecrackerIssue.bduni_objet_attribut_5.replace("'", "''") + "'") if osmosecrackerIssue.bduni_objet_attribut_5 else 'NULL',
                        espaceco_signalement_id=(osmosecrackerIssue.espaceco_signalement_id.replace("'", "''") + "'") if osmosecrackerIssue.espaceco_signalement_id else 'NULL',
                        espaceco_signalement_status=("'" + osmosecrackerIssue.espaceco_signalement_status + "'") if osmosecrackerIssue.espaceco_signalement_status else 'NULL',
                        espaceco_signalement_status_refresh_timestamp=("'" + osmosecrackerIssue.espaceco_signalement_status_refresh_timestamp.isoformat()+"'") if osmosecrackerIssue.espaceco_signalement_status_refresh_timestamp else 'NULL',
                        bduni_objet_zicad=("'" + osmosecrackerIssue.bduni_zicad.replace("'", "''") + "'") if osmosecrackerIssue.bduni_zicad else 'NULL',
                        core_classe_bduni=("'" + osmosecrackerIssue.core_classe_bduni.replace("'", "''") + "'") if osmosecrackerIssue.core_classe_bduni else 'NULL',
                        bduni_objet_date_modification=("'"+osmosecrackerIssue.bduni_objet_date_modification.replace("'", "''") + "'") if osmosecrackerIssue.bduni_objet_date_modification else 'NULL'
                    )
                    cur.execute(sql)
                    row = cur.fetchone()
                    (result, ) = row if row else None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, insertion impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'insertion d'un objet issue dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(osmosecrackerIssue),
                    str(exc)))
            raise
        else:
            return result
        finally:
            LOGGER.debug(
                "Insertion/sauvegarde de l'objet Osmose,"
                "opération réussie: {0}".format(str(result is not None)))

    def insert_core(self, osmosecrackerIssue: osmosecracker_issue.OsmoseCrackerIssue) -> int:
        """Fonction d'insertion de l'objet Osmose,
        uniquementson sous-ensemble principal.

        Keyword arguments:
            osmosecrackerIssue, objet de la classe
            osmosecracker_issue.OsmoseCrackerIssue,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'insertion.
        """
        result = None
        LOGGER.debug(
            "Insertion/sauvegarde de l'objet Osmose, "
            "caractéristiques principales")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    cur = sqlite3connection.cursor()
                    sql = """
                        INSERT INTO osmoseissue(
                        core_id,
                        core_status,
                        core_lat,
                        core_lon,
                        core_item_id,
                        core_item_name_auto,
                        core_item_name_fr,
                        core_source,
                        core_class_id,
                        core_class_name_auto,
                        core_class_name_fr,
                        core_subtitle,
                        core_country,
                        core_level,
                        core_update_timestamp,
                        core_usernames,
                        core_osm_ids_elems,
                        core_osm_ids_nodes,
                        core_osm_ids_ways,
                        core_osm_ids_relations,
                        core_classe_bduni
                        ) VALUES
                        (
                        {core_id},
                        {core_status},
                        {core_lat},
                        {core_lon},
                        {core_item_id},
                        {core_item_name_auto},
                        {core_item_name_fr},
                        {core_source},
                        {core_class_id},
                        {core_class_name_auto},
                        {core_class_name_fr},
                        {core_subtitle},
                        {core_country},
                        {core_level},
                        {core_update_timestamp},
                        {core_usernames},
                        {core_osm_ids_elems},
                        {core_osm_ids_nodes},
                        {core_osm_ids_ways},
                        {core_osm_ids_relations},
                        {core_classe_bduni}
                        ) RETURNING rowid;
                    """.format(
                        core_id=("'" + osmosecrackerIssue.core_id + "'"),
                        core_status=("'" + osmosecrackerIssue.core_status + "'"),
                        core_lat=osmosecrackerIssue.core_lat,
                        core_lon=osmosecrackerIssue.core_lon,
                        core_item_id=osmosecrackerIssue.core_item_id,
                        core_item_name_auto=("'" + osmosecrackerIssue.core_item_name_auto + "'") if osmosecrackerIssue.core_item_name_auto else 'NULL',
                        core_item_name_fr=("'" + osmosecrackerIssue.core_item_name_fr + "'") if osmosecrackerIssue.core_item_name_fr else 'NULL',
                        core_source=osmosecrackerIssue.core_source,
                        core_class_id=osmosecrackerIssue.core_class_id,
                        core_class_name_auto=("'" + osmosecrackerIssue.core_class_name_auto.replace("'", "''") + "'") if osmosecrackerIssue.core_class_name_auto else 'NULL',
                        core_class_name_fr=("'" + osmosecrackerIssue.core_class_name_fr.replace("'", "''") + "'") if osmosecrackerIssue.core_class_name_fr else 'NULL',
                        core_subtitle=("'" + osmosecrackerIssue.core_subtitle.replace("'", "''")+"'") if osmosecrackerIssue.core_subtitle else 'NULL',
                        core_country=("'" + osmosecrackerIssue.core_country+"'") if osmosecrackerIssue.core_country else 'NULL',
                        core_level=osmosecrackerIssue.core_level,
                        core_update_timestamp=("'" + osmosecrackerIssue.core_update_timestamp.isoformat() + "'"),
                        core_usernames=("'"+osmosecrackerIssue.core_usernames+"'") if osmosecrackerIssue.core_usernames else 'NULL',
                        core_osm_ids_elems=("'" + ','.join(str(osmosecrackerIssue.core_osm_ids_elems)) + "'") if osmosecrackerIssue.core_osm_ids_elems else 'NULL',
                        core_osm_ids_nodes=("'" + ','.join(str(osmosecrackerIssue.core_osm_ids_nodes)) + "'") if osmosecrackerIssue.core_osm_ids_nodes else 'NULL',
                        core_osm_ids_ways=("'" + ','.join(str(osmosecrackerIssue.core_osm_ids_ways)) + "'") if osmosecrackerIssue.core_osm_ids_ways else 'NULL',
                        core_osm_ids_relations=("'" + ','.join(str(osmosecrackerIssue.core_osm_ids_relations)) + "'") if osmosecrackerIssue.core_osm_ids_relations else 'NULL',
                        core_classe_bduni=("'" + osmosecrackerIssue.core_classe_bduni.isoformat() + "'")
                    )
                    LOGGER.debug(sql)
                    cur.execute(sql)
                    row = cur.fetchone()
                    (result, ) = row if row else None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, insertion impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'insertion d'un objet issue dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(osmosecrackerIssue),
                    str(exc)))
            raise
        else:
            return result
        finally:
            LOGGER.debug(
                "Insertion/sauvegarde de l'objet Osmose, "
                "caractéristiques principales, opération réussie: {0}".format(
                    str(result is not None)))

    def update_details(self, osmosecrackerIssue: osmosecracker_issue.OsmoseCrackerIssue) -> int:
        """Fonction d'update de l'objet Osmose,
        uniquement son sous-ensemble secondaire.

        Keyword arguments:
            osmosecrackerIssue, objet de la classe
            osmosecracker_issue.OsmoseCrackerIssue,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'update.
        """
        result = None
        LOGGER.debug(
            "Insertion/sauvegarde de l'objet Osmose, "
            "caractéristiques complémentaires")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    cur = sqlite3connection.cursor()
                    sql = """
                        UPDATE osmoseissue SET
                        details_descriptionstr = {details_descriptionstr},
                        details_minlat = {details_minlat},
                        details_maxlat = {details_maxlat},
                        details_minlon = {details_minlon},
                        details_maxlon = {details_maxlon},
                        details_b_date_datetime = {details_b_date_datetime},
                        details_osm_json_nodes = {details_osm_json_nodes},
                        details_osm_json_ways = {details_osm_json_ways},
                        details_osm_json_relations = {details_osm_json_relations},
                        details_new_elemns = {details_new_elemns},
                        osm_objects = {osm_objects},
                        bduni_zone_collecte_collecteur = {bduni_zone_collecte_collecteur},
                        espaceco_theme = {espaceco_theme},
                        bduni_commune_code_insee = {bduni_commune_code_insee},
                        bduni_commune_nom_officiel = {bduni_commune_nom_officiel},
                        bduni_canton_code_insee = {bduni_canton_code_insee},
                        bduni_arrondissement_code_insee = {bduni_arrondissement_code_insee},
                        bduni_arrondissement_nom_officiel = {bduni_arrondissement_nom_officiel},
                        bduni_collectivite_terr_code_insee = {bduni_collectivite_terr_code_insee},
                        bduni_collectivite_terr_nom_officiel = {bduni_collectivite_terr_nom_officiel},
                        bduni_departement_code_insee = {bduni_departement_code_insee},
                        bduni_departement_nom_officiel = {bduni_departement_nom_officiel},
                        bduni_region_code_insee = {bduni_region_code_insee},
                        bduni_region_nom_officiel = {bduni_region_nom_officiel},
                        bduni_territoire_nom = {bduni_territoire_nom},
                        bduni_territoire_srid  = {bduni_territoire_srid},
                        bduni_x = {bduni_x},
                        bduni_y  = {bduni_y},
                        bduni_object_cleabs = {bduni_object_cleabs},
                        bduni_objet_attribut_1 = {bduni_objet_attribut_1},
                        bduni_objet_attribut_2 = {bduni_objet_attribut_2},
                        bduni_objet_attribut_3 = {bduni_objet_attribut_3},
                        bduni_objet_attribut_4 = {bduni_objet_attribut_4},
                        bduni_objet_attribut_5 = {bduni_objet_attribut_5},
                        bduni_objet_zicad = {bduni_objet_zicad}
                        bduni_objet_date_modification = {bduni_objet_date_modification}
                        WHERE core_id = {core_id}
                        RETURNING rowid;
                    """.format(
                        core_id=osmosecrackerIssue.core_id,
                        details_descriptionstr=osmosecrackerIssue.details_descriptionstr.replace("'","''"),
                        details_minlat=osmosecrackerIssue.details_minlat,
                        details_maxlat=osmosecrackerIssue.details_maxlat,
                        details_minlon=osmosecrackerIssue.details_minlon,
                        details_maxlon=osmosecrackerIssue.details_maxlon,
                        details_b_date_datetime=osmosecrackerIssue.details_b_date_datetime,
                        details_osm_json_nodes=osmosecrackerIssue.details_osm_json_nodes,
                        details_osm_json_ways=osmosecrackerIssue.details_osm_json_ways,
                        details_osm_json_relations=osmosecrackerIssue.details_osm_json_relations,
                        details_new_elemns=osmosecrackerIssue.details_new_elemns,
                        osm_objects=osmosecrackerIssue.osm_objects,
                        bduni_zone_collecte_collecteur=osmosecrackerIssue.bduni_zone_collecte_collecteur,
                        espaceco_theme=osmosecrackerIssue.espaceco_theme,
                        bduni_commune_code_insee =osmosecrackerIssue.bduni_commune_code_insee,
                        bduni_commune_nom_officiel =osmosecrackerIssue.bduni_commune_nom_officiel.replace("'","''"),
                        bduni_canton_code_insee=osmosecrackerIssue.bduni_canton_code_insee,
                        bduni_arrondissement_code_insee=osmosecrackerIssue.bduni_arrondissement_code_insee,
                        bduni_arrondissemen_nom_officiel =osmosecrackerIssue.bduni_arrondissemen_nom_officiel.replace("'","''"),
                        bduni_collectivite_terr_code_inse =osmosecrackerIssue.bduni_collectivite_terr_code_inse,
                        bduni_collectivite_terr_nom_officiel=osmosecrackerIssue.bduni_collectivite_terr_nom_officiel.replace("'","''"),
                        bduni_departement_code_insee=osmosecrackerIssue.bduni_departement_code_insee,
                        bduni_departement_nom_officiel=osmosecrackerIssue.bduni_departement_nom_officiel,
                        bduni_region_code_insee=osmosecrackerIssue.bduni_region_code_insee,
                        bduni_region_nom_officiel=osmosecrackerIssue.bduni_region_nom_officiel.replace("'","''"),
                        bduni_territoire_nom=osmosecrackerIssue.bduni_territoire_nom.replace("'","''"),
                        bduni_territoire_srid=osmosecrackerIssue.bduni_territoire_srid,
                        bduni_x=osmosecrackerIssue.bduni_x,
                        bduni_y=osmosecrackerIssue.bduni_y,
                        bduni_object_cleabs = osmosecrackerIssue.bduni_object_cleabs.replace("'","''"),
                        bduni_objet_attribut_1 = osmosecrackerIssue.bduni_objet_attribut_1.replace("'","''"),
                        bduni_objet_attribut_2 = osmosecrackerIssue.bduni_objet_attribut_2.replace("'","''"),
                        bduni_objet_attribut_3 = osmosecrackerIssue.bduni_objet_attribut_3.replace("'","''"),
                        bduni_objet_attribut_4 = osmosecrackerIssue.bduni_objet_attribut_4.replace("'","''"),
                        bduni_objet_attribut_5 = osmosecrackerIssue.bduni_objet_attribut_5.replace("'","''"),
                        bduni_objet_zicad = osmosecrackerIssue.bduni_zicad.replace("'","''"),
                        bduni_objet_date_modification = osmosecrackerIssue.bduni_objet_date_modification.replace("'","''")
                    )
                    cur.execute(sql)
                    row = cur.fetchone()
                    (result, ) = row if row else None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'update d'un objet issue dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(osmosecrackerIssue),
                    str(exc)))
            raise
        else:
            return result
        finally:
            LOGGER.debug(
                "Insertion/sauvegarde de l'objet Osmose, "
                "caractéristiques complémentaires, "
                "opération réussie: {0}".format(str(result is not None)))

    def update_signalement(self, osmosecrackerIssue: osmosecracker_issue.OsmoseCrackerIssue) -> int:
        """Fonction d'update de l'objet Osmose,
        uniquement sur son attribut identifiant de signalement de l'espace collaboratif.

        Keyword arguments:
            osmosecrackerIssue, objet de la classe
            osmosecracker_issue.osmosecrackerIssue,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'update.
        """
        result = None
        LOGGER.debug("Mise à jour de l'identifiant EspaceCo de l'objet Osmose")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    cur = sqlite3connection.cursor()
                    sql = """
                        UPDATE osmoseissue SET
                        espaceco_signalement_id = {espaceco_signalement_id},
                        espaceco_signalement_status = '{espaceco_signalement_status}',
                        espaceco_signalement_status_refresh_timestamp = '{espaceco_signalement_status_refresh_timestamp}'
                        WHERE core_id = '{core_id}'
                        RETURNING rowid;
                    """.format(
                        core_id=osmosecrackerIssue.core_id,
                        espaceco_signalement_id=osmosecrackerIssue.espaceco_signalement_id,
                        espaceco_signalement_status=osmosecrackerIssue.espaceco_signalement_status,
                        espaceco_signalement_status_refresh_timestamp=osmosecrackerIssue.espaceco_signalement_status_refresh_timestamp.isoformat()
                    )
                    cur.execute(sql)
                    row = cur.fetchone()
                    (result, ) = row if row else None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'update d'un objet issue dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(osmosecrackerIssue),
                    str(exc)))
            raise
        else:
            return result
        finally:
            LOGGER.debug(
                "Mise à jour du statut EspaceCo de l'objet Osmose, "
                "opération réussie: {0}".format(str(result is not None)))

    def update_status(self, osmosecrackerIssue: osmosecracker_issue.OsmoseCrackerIssue) -> int:
        """Fonction d'update de l'objet Osmose,
        uniquement sur son sous-ensemble de status de
        signalement de l'espace collaboratif.

        Keyword arguments:
            osmosecrackerIssue, objet de la classe
            osmosecracker_issue.osmosecrackerIssue,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'update.
        """
        result = None
        LOGGER.debug("Mise à jour du statut EspaceCo de l'objet Osmose")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    cur = sqlite3connection.cursor()
                    sql = """
                        UPDATE osmoseissue SET
                        espaceco_signalement_status = {espaceco_signalement_status},
                        espaceco_signalement_status_refresh_timestamp = {espaceco_signalement_status_refresh_timestamp}
                        WHERE core_id = '{core_id}'
                        RETURNING rowid;
                    """.format(
                        core_id=osmosecrackerIssue.core_id,
                        espaceco_signalement_status=osmosecrackerIssue.espaceco_signalement_status,
                        espaceco_signalement_status_refresh_timestamp=osmosecrackerIssue.espaceco_signalement_status_refresh_timestamp.isoformat()
                    )
                    cur.execute(sql)
                    row = cur.fetchone()
                    (result, ) = row if row else None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'update d'un objet issue dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(exc),
                    str(osmosecrackerIssue)))
            raise
        else:
            return result
        finally:
            LOGGER.debug(
                "Mise à jour du statut EspaceCo de l'objet Osmose, "
                "opération réussie: {0}".format(str(result is not None)))
      
    def update_zicad(self, osmosecrackerIssue: osmosecracker_issue.OsmoseCrackerIssue) -> bool:
        """Fonction d'update de l'attribut zicad de l'objet issue entré en paramètre,

        Keyword arguments:
            osmosecrackerIssue, objet de la classe
            osmosecracker_issue.osmosecrackerIssue,
            contenant les informations à insérer,
            dont l'information bduni_zicad à mettre
            à jour dans la base locale sqlite
            pour le core_id de l'objet.  
        
        Returns:
            True si l'opération réussit.
        """
        result = False
        LOGGER.debug("Mise à jour du statut zicad de l'objet")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    cur = sqlite3connection.cursor()
                    sql = """
                        UPDATE osmoseissue SET
                        bduni_objet_zicad = {zicad_status}
                        WHERE core_id = '{core_id}'
                        RETURNING rowid;
                    """.format(
                        core_id=str(osmosecrackerIssue.core_id),
                        zicad_status=osmosecrackerIssue.bduni_zicad
                    )
                    cur.execute(sql)
                    row = cur.fetchone()
                    sqlite3connection.commit()
                    result = True
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'update d'un objet issue dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(exc),
                    str(osmosecrackerIssue)))
            raise
        else:
            return result
        finally:
            LOGGER.debug(
                "Mise à jour du statut zicad de l'objet Osmose, "
                "opération réussie: {0}".format(str(result is not None)))

    def _issue_row_to_issue_instance(self, issueRow: sqlite3.Row) -> osmosecracker_issue.OsmoseCrackerIssue:
        """Fonction d'instanciation de deserialisation d'une issue.

        Keyword arguments:
            issueRow, objet de la classe sqlite3.Row, contenant les informations serialisées permettant
            d'instancier une issue de la classe osmosecracker_issue.OsmoseCrackerIssue.

        Returns:
            Instance d'osmosecracker_issue.OsmoseCrackerIssue.
        """
        
        issue_instance = osmosecracker_issue.OsmoseCrackerIssue(
                 uuid=str(issueRow["core_id"]),
                 status=str(issueRow["core_status"]),
                 source=int(issueRow["core_source"]),
                 item=int(issueRow["core_item_id"]),
                 item_name_auto=str(issueRow["core_item_name_auto"]),
                 item_name_fr=str(issueRow["core_item_name_fr"]),
                 classe=int(issueRow["core_class_id"]),
                 class_name_auto=str(issueRow["core_class_name_auto"]),
                 class_name_fr=str(issueRow["core_class_name_fr"]),
                 level=int(issueRow["core_level"]),
                 subtitle=str(issueRow["core_subtitle"]),
                 country=str(issueRow["core_country"]),
                 timestamp=datetime.datetime.fromisoformat(issueRow["core_update_timestamp"]),
                 username=str(issueRow["core_usernames"]),
                 lat=float(issueRow["core_lat"]),
                 lon=float(issueRow["core_lon"]),
                 elems=str(issueRow["core_osm_ids_elems"]),
                 espaceco_theme = str(issueRow["espaceco_theme"]),
                 core_classe_bduni = str(issueRow["core_classe_bduni"])
                 )
        issue_instance.core_osm_ids_nodes = str(issueRow["core_osm_ids_nodes"])
        issue_instance.core_osm_ids_ways = str(issueRow["core_osm_ids_ways"])
        issue_instance.core_osm_ids_relations = str(issueRow["core_osm_ids_relations"])
        issue_instance.details_descriptionstr = str(issueRow["details_descriptionstr"])
        issue_instance.details_minlat = float(issueRow["details_minlat"]) if issueRow["details_minlat"] else None
        issue_instance.details_maxlat = float(issueRow["details_maxlat"]) if issueRow["details_maxlat"] else None
        issue_instance.details_minlon = float(issueRow["details_minlon"]) if issueRow["details_minlon"] else None
        issue_instance.details_maxlon = float(issueRow["details_maxlon"]) if issueRow["details_maxlon"] else None
        issue_instance.details_b_date_datetime = datetime.datetime.fromisoformat(issueRow["details_b_date_datetime"]) if issueRow["details_b_date_datetime"] else None
        issue_instance.details_osm_json_nodes = {str(issueRow["details_osm_json_nodes"]).split(",")} if issueRow["details_osm_json_nodes"] else None
        issue_instance.details_osm_json_ways = {str(issueRow["details_osm_json_ways"]).split(",")} if issueRow["details_osm_json_ways"] else None
        issue_instance.details_osm_json_relations = {str(issueRow["details_osm_json_relations"]).split(",")} if issueRow["details_osm_json_relations"] else None
        issue_instance.details_new_elemns = {str(issueRow["details_new_elemns"]).split(",")} if issueRow["details_new_elemns"] else None
        issue_instance.osm_objects = str(issueRow["osm_objects"]) if issueRow["osm_objects"] else None
        issue_instance.bduni_zone_collecte_collecteur = str(issueRow["bduni_zone_collecte_collecteur"]) if issueRow["bduni_zone_collecte_collecteur"] else None
        issue_instance.bduni_commune_code_insee = str(issueRow["bduni_commune_code_insee"]) if issueRow["bduni_commune_code_insee"] else None
        issue_instance.bduni_commune_nom_officiel = str(issueRow["bduni_commune_nom_officiel"]) if issueRow["bduni_commune_nom_officiel"] else None
        issue_instance.bduni_canton_code_insee = str(issueRow["bduni_canton_code_insee"]) if issueRow["bduni_canton_code_insee"] else None
        issue_instance.bduni_arrondissement_code_insee = str(issueRow["bduni_arrondissement_code_insee"]) if issueRow["bduni_arrondissement_code_insee"] else None
        issue_instance.bduni_arrondissement_nom_officiel = str(issueRow["bduni_arrondissement_nom_officiel"]) if issueRow["bduni_arrondissement_nom_officiel"] else None
        issue_instance.bduni_collectivite_terr_code_insee = str(issueRow["bduni_collectivite_terr_code_insee"]) if issueRow["bduni_collectivite_terr_code_insee"] else None
        issue_instance.bduni_collectivite_terr_nom_officiel = str(issueRow["bduni_collectivite_terr_nom_officiel"]) if issueRow["bduni_collectivite_terr_nom_officiel"] else None
        issue_instance.bduni_departement_code_insee = str(issueRow["bduni_departement_code_insee"]) if issueRow["bduni_departement_code_insee"] else None
        issue_instance.bduni_departement_nom_officiel = str(issueRow["bduni_departement_nom_officiel"]) if issueRow["bduni_departement_nom_officiel"] else None
        issue_instance.bduni_region_code_insee = str(issueRow["bduni_region_code_insee"]) if issueRow["bduni_region_code_insee"] else None
        issue_instance.bduni_region_nom_officiel = str(issueRow["bduni_region_nom_officiel"]) if issueRow["bduni_region_nom_officiel"] else None
        issue_instance.bduni_territoire_nom = str(issueRow["bduni_territoire_nom"]) if issueRow["bduni_territoire_nom"] else None
        issue_instance.bduni_territoire_srid = int(issueRow["bduni_territoire_srid"]) if issueRow["bduni_territoire_srid"] else None
        issue_instance.bduni_x = float(issueRow["bduni_x"]) if issueRow["bduni_x"] else None
        issue_instance.bduni_y = float(issueRow["bduni_y"]) if issueRow["bduni_y"] else None
        issue_instance.bduni_object_cleabs = str(issueRow["bduni_object_cleabs"]) if issueRow["bduni_object_cleabs"] else None
        issue_instance.bduni_objet_attribut_1 = str(issueRow["bduni_objet_attribut_1"]) if issueRow["bduni_objet_attribut_1"] else None
        issue_instance.bduni_objet_attribut_2 = str(issueRow["bduni_objet_attribut_2"]) if issueRow["bduni_objet_attribut_2"] else None
        issue_instance.bduni_objet_attribut_3 = str(issueRow["bduni_objet_attribut_3"]) if issueRow["bduni_objet_attribut_3"] else None
        issue_instance.bduni_objet_attribut_4 = str(issueRow["bduni_objet_attribut_4"]) if issueRow["bduni_objet_attribut_4"] else None
        issue_instance.bduni_objet_attribut_5 = str(issueRow["bduni_objet_attribut_5"]) if issueRow["bduni_objet_attribut_5"] else None 
        issue_instance.espaceco_signalement_id = int(issueRow["espaceco_signalement_id"]) if issueRow["espaceco_signalement_id"] else None
        issue_instance.espaceco_signalement_status = str(issueRow["espaceco_signalement_status"]) if issueRow["espaceco_signalement_status"] else None
        issue_instance.espaceco_signalement_status_refresh_timestamp = datetime.datetime.fromisoformat(issueRow["espaceco_signalement_status_refresh_timestamp"]) if issueRow["espaceco_signalement_status_refresh_timestamp"] else None
        issue_instance.bduni_zicad = str(issueRow["bduni_objet_zicad"]) if issueRow["bduni_objet_zicad"] else None        
        issue_instance.bduni_objet_date_modification = str(issueRow["bduni_objet_date_modification"]) if issueRow["bduni_objet_date_modification"] else None
        return issue_instance 

    def get_issue_by_osmose_uuid(self, osmose_uuid: uuid.UUID) -> osmosecracker_issue.OsmoseCrackerIssue:
        """Fonction de requête d'un objet osmose sauvé localement,
        selon son uuid Osmose.

        Keyword arguments:
            Uuid de l'objet recherché.

        Returns:
            None ou osmosecrackerIssue,
            objet de la classe osmosecracker_issue.OsmoseCrackerIssue.
        """
        result = None
        LOGGER.debug(
            "Lecture de l'objet Osmose enregistré localement, "
            "selon son uuid Osmose {id} ".format(id=str(osmose_uuid)))
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        SELECT * FROM osmoseissue
                        WHERE core_id = '{core_id}' ;
                        """.format(
                            core_id=str(osmose_uuid)
                        )
                    cur.execute(sql)
                    row = cur.fetchone()
                    issue_row = row if row else None
                    if issue_row is not None:
                        result = self._issue_row_to_issue_instance(issue_row)
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur au requetage de l'objet"
                " d'UUID={0}.".format(str(osmose_uuid)))
            raise exc
        else:
            return result
        finally:
            LOGGER.debug(
                "Lecture de l'objet Osmose enregistré localement, "
                "selon son uuid Osmose, "
                "opération réussie: {0}".format(str(result is not None)))

    def get_issue_by_espacecosignalement_id(self, espacecosignalement_id: int) -> osmosecracker_issue.OsmoseCrackerIssue:
        """Fonction de requête d'un objet osmose sauvé localement,
        selon son id espace collaboratif.

        Keyword arguments:
            Id EspaceCo de l'objet recherché.

        Returns:
            None ou osmosecrackerIssue,
            objet de la classe osmosecracker_issue.OsmoseCrackerIssue.
        """
        result = None
        LOGGER.info(
            "Lecture de l'objet Osmose enregistré localement, "
            "selon son id de signalement EspaceCo {id}".format(id=str(espacecosignalement_id)))
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        SELECT * FROM osmoseissue
                        WHERE espaceco_signalement_id = {espaceco_signalement_id} ;
                        """.format(
                            espaceco_signalement_id=str(espacecosignalement_id)
                        )
                    cur.execute(sql)
                    row = cur.fetchone()
                    issue_row = row if row else None
                    if issue_row is not None:
                        result = self._issue_row_to_issue_instance(issue_row)
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur au requetage de l'objet"
                " d'espacecosignalement_id={0}.".format(
                    str(espacecosignalement_id)))
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Lecture de l'objet Osmose enregistré localement, "
                "selon son id de signalement EspaceCo, "
                "opération réussie: {0}".format(str(result is not None)))
               
    def get_issues_where_zicad_null(self) -> [osmosecracker_issue.OsmoseCrackerIssue]:
        """Fonction de requête des objets osmoses sauvés localement,
        avec information sur zicad = NULL.

        Keyword arguments:

        Returns:
            None ou liste de osmosecrackerIssue,
            objets de la classe osmosecracker_issue.OsmoseCrackerIssue.
        """
        result = []
        LOGGER.info(
            "Lecture des objets Osmose enregistrés localement, "
            "avec zicad = NULL")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        SELECT * FROM osmoseissue
                        WHERE bduni_objet_zicad IS NULL ;
                        """
                    cur.execute(sql)
                    issue_rows = cur.fetchall()
                    for issue_row in issue_rows:
                        result.append(self._issue_row_to_issue_instance(issue_row))
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur au requetage des issues zicad"
                " = NULL")
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Lecture des objets Osmose enregistrés localement, "
                "avec zical = NULL "
                "opération réussie: {0}, n={1}".format(
                str(result is not None),
                str(len(result) if result else 0)))

    def get_issues_by_espacecosignalements_unclosed(self) -> [osmosecracker_issue.OsmoseCrackerIssue]:
        """Fonction de requête des objets osmoses sauvés localement,
        de statut différent de clos.

        Keyword arguments:

        Returns:
            None ou liste de osmosecrackerIssue,
            objets de la classe osmosecracker_issue.OsmoseCrackerIssue.
        """
        result = []
        LOGGER.info(
            "Lecture des objets Osmose enregistrés localement, "
            "de statut EspaceCo <> clos soit [{0}].".format(','.join(osmosecracker_config.OC_UNCLOSED_STATUSES)))
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        SELECT * FROM osmoseissue
                        WHERE espaceco_signalement_status NOT IN ({espaceco_signalement_status}) ;
                        """.format(
                            espaceco_signalement_status=', '.join(f'"{us}"' for us in osmosecracker_config.OC_UNCLOSED_STATUSES)
                        )
                    cur.execute(sql)
                    issue_rows = cur.fetchall()
                    for issue_row in issue_rows:
                        result.append(self._issue_row_to_issue_instance(issue_row))
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur au requetage des issues unclosed"
                " de status espaceco !={0}.".format(
                    str(','.join(osmosecracker_config.OC_UNCLOSED_STATUSES))))
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Lecture des objets Osmose enregistrés localement, "
                "de statut EspaceCo <> clos, "
                "opération réussie: {0}, n={1}".format(
                str(result is not None),
                str(len(result) if result else 0)))

    def get_issues_by_espacecosignalements_none(self) -> [osmosecracker_issue.OsmoseCrackerIssue]:
        """Fonction de requête des objets osmoses sauvés localement,
        n'ayant pas fait l'objet d'un signalement.

        Keyword arguments:

        Returns:
            None ou liste de osmosecrackerIssue,
            objets de la classe osmosecracker_issue.OsmoseCrackerIssue.
        """
        result = []
        LOGGER.info(
            "Lecture des objets Osmose enregistrés localement, "
            "de signalement id null")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        SELECT * FROM osmoseissue
                        WHERE espaceco_signalement_id IS NULL;
                        """
                    cur.execute(sql)
                    issue_rows = cur.fetchall()
                    for issue_row in issue_rows:
                        result.append(self._issue_row_to_issue_instance(issue_row))
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur au requetage des issues sans signalement id")
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Lecture des objets Osmose enregistrés localement, "
                "de statut signalement_id != null, "
                "opération réussie: {0}".format(str(result is not None)))

    def get_issues_by_espacecosignalements_none_and_zicad_false(self) -> [osmosecracker_issue.OsmoseCrackerIssue]:
        """Fonction de requête des objets osmoses sauvés localement,
        n'ayant pas fait lk'objet d'un signalement EspaceCo
        et n'étant pas situé dans une ZICAD.

        Keyword arguments:

        Returns:
            None ou liste de osmosecrackerIssue,
            objets de la classe osmosecracker_issue.OsmoseCrackerIssue.
        """
        result = []
        LOGGER.info(
            "Lecture des objets Osmose enregistrés localement, "
            "de signalement id null et zicad false")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        SELECT * FROM osmoseissue
                        WHERE espaceco_signalement_id is null
                        AND NOT bduni_objet_zicad;
                        """
                    cur.execute(sql)
                    issue_rows = cur.fetchall()
                    for issue_row in issue_rows:
                        result.append(self._issue_row_to_issue_instance(issue_row))
            else:
                raise ValueError("Base SQLite invalide, update impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur au requetage des issues sans signalement id et hors zicad")
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Lecture des objets Osmose enregistrés localement, "
                "de statut signalement_id != null, "
                "n'étant pas situé dans une zicad"
                "opération réussie: {0}".format(str(result is not None)))

    def backup(self, backupFilePath: pathlib.PurePath) -> bool:
        """Fonction de sauvegarde de la base SQLite.

        Keyword arguments:
            backupFilePath, chemin pathlib.PurePath,
            où sauvegarder la base SQLite.

        Returns:
            Boolean indicateur de la bonne exécution.
        """
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup
        result = False
        LOGGER.info("Backup de la base de donnée SQLite.")
        try:
            if self.is_valid():
                if exportFilePath.is_absolute():
                    if os.access(
                        str(exportFolderPath.resolve().parent),
                            os.W_OK):
                        if exportFilePath.suffix == '.sqlite':
                            if not exportFilePath.exists:
                                src = sqlite3.connect(
                                    self.self.databaseFilePath)
                                dst = sqlite3.connect(backupFilePath)
                                with dst:
                                    src.backup(dst)
                                dst.close()
                                src.close()
                                result = True
                            else:
                                raise ValueError(
                                    "Fichier de même nom déjà existant, "
                                    "backup impossible")
                        else:
                            raise ValueError(
                                "Suffixe non .sqlite, "
                                "backup impossible")
                    else:
                        raise ValueError(
                            "Répertoire non accessible en écriture, "
                            "backup impossible")
                else:
                    raise ValueError(
                        "Chemin base SQLite non absolu, "
                        "backup impossible")
            else:
                raise ValueError("Base SQLite invalide, backup impossible")
        except Exception as exc:
            LOGGER.exception("Erreur à la sauvegarde, {0}".format(str(exc)))
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Backup de la base de donnée SQLite, "
                "opération réussie: {0}".format(str(result is not False)))


    def _exportlogic(self, exportFilePath: pathlib.PurePath,sql: str) -> bool:
        """Fonction d'export de la base SQLite.

        Keyword arguments:
            exportFolderPath, répertoire pathlib.PurePath,
            où exporter la base SQLite.

        Returns:
            Boolean indicateur de la bonne exécution.
        """
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(sql)
            columns = [column[0] for column in c.description]
            results = []
            for row in c.fetchall():
                results.append(dict(zip(columns, row)))
            with open(str(exportFilePath), "w", newline='') as new_file:
                fieldnames = columns
                writer = csv.DictWriter(new_file, fieldnames=fieldnames)
                writer.writeheader()
            for line in results:
                writer.writerow(line)
            conn.close()

    def export(self, exportFolderPath: pathlib.PurePath) -> bool:
        """Fonction d'export de la base SQLite.

        Keyword arguments:
            exportFolderPath, répertoire pathlib.PurePath
            où exporter la base SQLite.

        Returns:
            Boolean indicateur de la bonne exécution.
        """
        result = False
        LOGGER.info("Export de la base de donnée SQLite sous {0}.".format(
            str(exportFolderPath)))
        try:
            if self.is_valid():
                if exportFolderPath.is_absolute():
                    if exportFolderPath.is_dir():
                        timestamp = datetime.datetime.now().strftime(
                            "%Y%m%d-%H%M%S")
                        if os.access(str(exportFolderPath), os.W_OK):
                            sql = "SELECT rowid, * FROM osmoseissue"
                            self._exportlogic(exportFolderPath.joinpath(
                                'OSMOSECracker_{timestamp}_issues.csv'.format(
                                    timestamp)), sql)
                            sql = "SELECT rowid, * FROM workflowexecutions"
                            self._exportlogic(exportFolderPath.joinpath(
                                'OSMOSECracker_{timestamp}_workflowexecutions.csv'.format(
                                    timestamp)), sql)
                            result = True
                        else:
                            raise ValueError(
                                "Export impossible, répertoire {0} "
                                "inaccessible en écriture.".format(
                                    str(exportFolderPath)))
                    else:
                        raise ValueError(
                            "Export impossible, répertoire {0} "
                            "n'est pas un répertoire.".format(
                                str(exportFolderPath)))
                else:
                    raise ValueError(
                        "Export impossible, répertoire {0} "
                        "n'est pas path absolu.".format(
                            str(exportFolderPath)))
            else:
                raise ValueError("Base SQLite invalide, export impossible")
        except Exception as exc:
            LOGGER.exception("Erreur à l'export, {0}".format(str(exc)))
            raise exc
        else:
            return result
        finally:
            LOGGER.info(
                "Backup de la base de donnée SQLite, "
                "opération réussie: {0}".format(str(result is not False)))


    def workflow_insert(
        self,
            Workflow: 'osmosecracker_workflow._osmosecrackerworkflow') -> int:
        """Fonction d'insertion de l'objet Workflow.

        Keyword arguments:
            Workflow, objet de la classe
            osmosecracker_workflow._osmosecrackerworkflow,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'insertion.
        """
        result = None
        LOGGER.debug(
            "Insertion/sauvegarde de l'objet Workflow")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        INSERT INTO workflowexecutions(
                            workflow_guuid,
                            workflow_parameters,
                            timestamp_workflow_start,
                            timestamp_issues_collecting_start,
                            timestamp_issues_collecting_end,
                            timestamp_details_uuid_added,
                            timestamp_workflow_end,
                            workflow_exception_log,
                            stats_issues_collected_count,
                            stats_issues_collected_new_count,
                            stats_issues_reported_count
                        ) VALUES
                        (
                        {workflow_guuid},
                        {workflow_parameters},
                        {timestamp_workflow_start},
                        {timestamp_issues_collecting_start},
                        {timestamp_issues_collecting_end},
                        {timestamp_details_uuid_added},
                        {timestamp_workflow_end},
                        {workflow_exception_log},
                        {stats_issues_collected_count},
                        {stats_issues_collected_new_count},
                        {stats_issues_reported_count}
                        ) RETURNING dbid;
                    """.format(
                        workflow_guuid=("'"+str(Workflow.workflow_guuid)+"'"),
                        workflow_parameters='NULL',
                        timestamp_workflow_start=("'"+Workflow.timestamp_workflow_start.isoformat()+"'"),
                        timestamp_issues_collecting_start='NULL',
                        timestamp_issues_collecting_end='NULL',
                        timestamp_details_uuid_added='NULL',
                        timestamp_workflow_end='NULL',
                        workflow_exception_log='NULL',
                        stats_issues_collected_count='NULL',
                        stats_issues_collected_new_count='NULL',
                        stats_issues_reported_count='NULL'
                    )
                    LOGGER.debug(sql)
                    cur.execute(sql)
                    row = cur.fetchone()
                    if row:
                        (result, ) = row
                    else:
                        result = None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, insertion impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'insertion d'un objet Workflow dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(Workflow),
                    str(exc)))
            raise
        else:
            return result
        finally:
            LOGGER.info(
                "Insertion/sauvegarde de l'objet Workflow, "
                "opération réussie: {0}".format(
                    str(result is not None)))

    def workflow_update(self, Workflow: 'osmosecracker_workflow._osmosecrackerworkflow') -> bool:
        """Fonction d'update de l'objet Workflow.

        Keyword arguments:
            osmosecrackerWorkflow, objet de la classe
            osmosecracker_workflow.osmosecrackerWorkflow,
            contenant les informations à insérer.

        Returns:
            None ou entier de l'id de l'update.
        """
        result = None
        LOGGER.debug("Update de l'objet Workflow")
        try:
            if self.is_valid():
                with sqlite3.connect(str(self.databaseFilePath)) as sqlite3connection:
                    sqlite3connection.row_factory = sqlite3.Row
                    cur = sqlite3connection.cursor()
                    sql = """
                        UPDATE workflowexecutions SET
                            workflow_parameters = {workflow_parameters},
                            timestamp_workflow_start = '{timestamp_workflow_start}',
                            timestamp_issues_collecting_start = {timestamp_issues_collecting_start},
                            timestamp_issues_collecting_end = {timestamp_issues_collecting_end},
                            timestamp_details_uuid_added = {timestamp_details_uuid_added},
                            timestamp_workflow_end = {timestamp_workflow_end},
                            workflow_exception_log = {workflow_exception_log},
                            stats_issues_collected_count = {stats_issues_collected_count},
                            stats_issues_collected_new_count = {stats_issues_collected_new_count},
                            stats_issues_reported_count = {stats_issues_reported_count}
                        WHERE workflow_guuid = '{workflow_guuid}'
                        RETURNING dbid;
                    """.format(
                        workflow_guuid=str(Workflow.workflow_guuid),
                        workflow_parameters=("'"+Workflow.workflow_parameters.replace("'","''")+"'") if Workflow.workflow_parameters else 'NULL',
                        timestamp_workflow_start=Workflow.timestamp_workflow_start.isoformat(),
                        timestamp_issues_collecting_start=("'"+Workflow.timestamp_issues_collecting_start.isoformat()+"'") if Workflow.timestamp_issues_collecting_start else 'NULL',
                        timestamp_issues_collecting_end=("'"+Workflow.timestamp_issues_collecting_end.isoformat()+"'") if Workflow.timestamp_issues_collecting_end else 'NULL',
                        timestamp_details_uuid_added=("'"+Workflow.timestamp_details_uuid_added.isoformat()+"'") if Workflow.timestamp_details_uuid_added else 'NULL',
                        timestamp_workflow_end=("'"+Workflow.timestamp_workflow_end.isoformat()+"'") if Workflow.timestamp_workflow_end else 'NULL',
                        workflow_exception_log=("'"+Workflow.workflow_exception_log.replace("'","''")+"'") if Workflow.workflow_exception_log else 'NULL',
                        stats_issues_collected_count=Workflow.stats_issues_collected_count if Workflow.stats_issues_collected_count else 'NULL',
                        stats_issues_collected_new_count=Workflow.stats_issues_collected_new_count if Workflow.stats_issues_collected_new_count else 'NULL',
                        stats_issues_reported_count=Workflow.stats_issues_reported_count if Workflow.stats_issues_reported_count else 'NULL'
                        )
                    cur.execute(sql)
                    row = cur.fetchone()
                    if row:
                        (result, ) = row
                    else:
                        result = None
                    sqlite3connection.commit()
            else:
                raise ValueError("Base SQLite invalide, insertion impossible")
        except Exception as exc:
            LOGGER.exception(
                "Erreur à l'insertion d'un objet Workflow dans la base"
                " SQLite {0}, objet: {1}, exc: {2}".format(
                    str(self.databaseFilePath),
                    str(Workflow),
                    str(exc)))
        else:
            return result
        finally:
            LOGGER.debug(
                "Insertion/sauvegarde de l'objet Workflow, "
                "opération réussie: {0}".format(
                    str(result is not None)))


# La commande qui explicite la singularité/singleton de la classe
osmosecrackerDatabase = _osmosecrackerDatabase()
