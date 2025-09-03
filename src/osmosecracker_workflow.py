#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# version ='1.1'
# ---------------------------------------------------------------------------
""" Classe singleton responsable de vehiculer et persister sqlite
    les informations du workflow.

    Usage:
    from osmosecracker_workflow import osmosecrackerWorkflow
    osmosecrackerWorkflow.create(TimestampStart)
"""
# ---------------------------------------------------------------------------

# Notes
# https://docs.python.org/3/library/sqlite3.html#sqlite3-connection-context-manager
# Singleton via module, cf. https://stackoverflow.com/a/52930277
# chaque modif d’attribut déclenche la persistance en base,
#  cf. https://stackoverflow.com/a/39730178

# Imports
import datetime
import logging
import uuid
from typing import Final, final, ClassVar
from osmosecracker_database_management import osmosecrackerDatabase
import osmosecracker_exceptions
import osmosecracker_issue

LOGGER = logging.getLogger('OsmoseCracker.Workflow')


class _osmosecrackerworkflow(object):
    """Classe singleton responsable de vehiculer et persister sqlite
    les informations du workflow."""

    workflow_guuid: uuid.UUID = None
    """ UUID du workflow """

    database_id: int = None
    """ Identifiant du workflow dans la base SQLite """

    workflow_parameters: str = None
    """ Les paramètres d'appel du script """

    timestamp_workflow_start: datetime.datetime = None
    """ Le timestamp de lancement du scipt """

    timestamp_issues_collecting_start: datetime.datetime = None
    """ Le timestamp de lancement de la requête osmose core. """

    timestamp_issues_collecting_end: datetime.datetime = None
    """ Le timestamp de fin de la requête osmose core. """

    timestamp_details_uuid_added: datetime.datetime = None
    """ Le timestamp de fin d'ajout des
    infos osmose uuid pour toutes les issues. """

    timestamp_workflow_end: datetime.datetime = None
    """ Le timestamp de fin de traitement. """

    workflow_duration_seconds: int = None
    """ Durée du traitement (sec) si exécution correcte, None sinon.
        A la fin du programme,
        timestamp_workflow_end - timestamp_workflow_start
    """
    workflow_exception_log: str = None
    """ En cas de plantage du programme,
    l'exception la plus proche de la cause. """

    stats_issues_collected_count: int = None
    """ Nombre d'issues Osmose requêtées par l'exécution du programme
    suivant les paramètres d'appel du script. """

    stats_issues_collected_new_count: int = None
    """ Nombre d'issues Osmose requêtées par l'exécution du programme
    suivant les paramètres d'appel du script et encore inconnues. """

    stats_issues_reported_count: int = None
    """ Nombre de nouveaux (issue Osmose inconnue jusqu'alors)
    signalements créés. """

    def __init__(self):
        """Crée et initialise l'instance de osmosecrackerWorkflow.

        Keyword arguments:

        Returns:
            Instance (singleton) de osmosecrackerWorkflow
        """
        LOGGER.info("Instanciation du singleton des informations du workflow.")
        self.workflow_guuid: Final = uuid.uuid4()
        self.timestamp_workflow_start: Final = (
            datetime.datetime.now())
        if not osmosecrackerDatabase.exists():
            osmosecrackerDatabase.create()
        if not osmosecrackerDatabase.is_valid():
            raise osmosecracker_exceptions.DatabaseInvalid(
                "Base nouvellement créée invalide.")
        database_id = osmosecrackerDatabase.workflow_insert(self)
        self.database_id: Final = database_id
        LOGGER.info(
            "Instanciation du singleton des informations du workflow OK.")

    def __setattr__(self, key: str, value):
        """ Surcharge de la fonction, pour y ajouter l'appel
        à notre fonction de persistance SQLite."""
        if getattr(self, key) is None:
            self.__dict__[key] = value
        elif key == 'stats_issues_reported_count':
            self.__dict__[key] = value
        else:
            raise osmosecracker_exceptions.WorkflowAttributesProtected(
                "key: {key}, value: {value}".format(key=key, value=value)
            )
        if not ((key == 'workflow_guuid') or (
                key == 'timestamp_workflow_start')):
            LOGGER.debug(
                "Workflow, update {0} de valeur {1}".format(
                    str(key), str(value)))
            osmosecrackerDatabase.workflow_update(self)
            LOGGER.debug(
                "Workflow, update {0} de valeur {1} persisté".format(
                    str(key), str(value)))
            
    def log_error(self, error: str):
        """ Lorsqu'une erreur se produit. """
        osmosecrackerWorkflow.timestamp_workflow_end = None
        osmosecrackerWorkflow.workflow_duration_seconds = None
        osmosecrackerWorkflow.workflow_exception_log  = error
        osmosecrackerDatabase.workflow_update(self)
        
# La commande qui explicite la singularité/singleton de la classe
osmosecrackerWorkflow = _osmosecrackerworkflow()
