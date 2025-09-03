#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Classes d'exception utilisées dans l'application.

Parameters
----------
Exception : 'Exception raised' 
    Contient le message d'erreur.

Retours
-------
LOGGER.critical(self.message) : 'error'
    Arrête le programme.
"""
# --------------------------------------------------------------------------- 
# Imports
import logging

LOGGER = logging.getLogger('osmosecracker_issue.Exceptions')


class WorkflowAttributesProtected(Exception):
    """Exception raised when we try to update an already defined
    attribute of workflow

    """
    def __init__(self, details: str):
        self.message = ("Attribut de workflow déjà mis à jour ; "
                        "re mise à jour interdite. "
                        "{details}".format(details=details))
        LOGGER.critical(self.message)


class DatabaseInvalid(Exception):
    """Exception raised when SQLite database is invalid.
    """
    def __init__(self, details: str):
        self.message = ("Base SQLite invalide. "
                        "{details}".format(details=details))
        LOGGER.critical(self.message)


class EspaceCoException(Exception):
    """Exception raised when something's wrong with EspaceCo.
    """
    def __init__(self, details: str):
        self.message = ("Post EspaceCo impossible. "
                        "{details}".format(details=details))
        LOGGER.critical(self.message)


#"*********"
# "*********"
# "*********"
# "*********"
# "*********"
#   "*********"
