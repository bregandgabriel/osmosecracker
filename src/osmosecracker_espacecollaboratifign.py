#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# Modif Date v1.1 : July 2024
# version ='1.1'
# ---------------------------------------------------------------------------
"""
Partie du programme chargée de faire tous les appels au serveur Espace Collaboratif.

Capable:
_d'émettre un signalement sur l'Espace Collaboratif
_de récupérer le statut de traitement de signalements
"""
# ---------------------------------------------------------------------------

# Notes
# https://espacecollaboratif.ign.fr/gcms/api/doc
# Copie du code de Grégorie

# Imports
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from urllib3 import encode_multipart_formdata
import osmosecracker_config
import osmosecracker_exceptions


LOGGER = logging.getLogger('OsmoseCracker.EspaceCollaboratif.EspaceCo')


def post_signalement(lon: float, 
                     lat: float, 
                     message: str, 
                     theme: str, 
                     type_signalement: str,
                     sketchcontent: str = None): #TODO NEW V1.1
    """
    Envoie un signalement dans l'Espace Collaboratif IGN.

    Keyword arguments:
    lon (float): Longitude du signalement
    lat (float): Latitude du signalement
    message (string): Contenu textuel du signalement
    theme (string): Groupe EspaceCo dans lequel poster le signalement
    type_signalement (string): test ou submit

    :return: Identifiant du signalement créé si signalement réussi, None sinon
    """
    createdid = None
    try:
        geometrie = "POINT({lon} {lat})".format(lon=str(lon), lat=str(lat))

        # Groupe BDUni d'id=1, sinon osmosecracker_config.OC_ESPACECO_GROUPE
        req_dict = {
            "community": osmosecracker_config.OC_ESPACECO_GROUPE,
            "geometry": geometrie,
            "comment": message,
            "status": 'submit' if (type_signalement == 'repost') else type_signalement,
            "input_device": "UNKNOWN",
            "device_version": "0.0",
            "attributes": {
                "community": osmosecracker_config.OC_ESPACECO_GROUPE,
                "theme": theme,
                "attributes": {}
                }
            }
        
        if sketchcontent != None: #TODO NEW V1.1
            req_dict['sketch'] = json.dumps(sketchcontent, indent=4)

        req = requests.post(url=osmosecracker_config.OC_ESPACECO_ENDPOINT,
                            proxies=osmosecracker_config.OC_PROXIES,
                            data=str(json.dumps(req_dict, indent=4)),
                            auth=HTTPBasicAuth(
                                osmosecracker_config.OC_ESPACECO_LOGIN,
                                osmosecracker_config.OC_ESPACECO_PWD))
        coderetour = req.status_code
        if coderetour == 201:
            createdid = req.json()['id']
        else:
            raise osmosecracker_exceptions.EspaceCoException(str(req.json()))
    except Exception as exc:
        LOGGER.error("Erreur lors de la requête POST "
                     "lors du signalement à l'espace collaboratif. \n"
                     + str(exc.message))
        raise exc
    else:
        return createdid


def get_status_signalement(signalement: int):
    """
    Récupère le statut d'un signalement dans l'Espace Collaboratif IGN.

    Keyword arguments:
    signalement (int): Identifiant du signalement

    :return: Status du signalement, None sinon
    """
    try:
        req = requests.get((osmosecracker_config.OC_ESPACECO_ENDPOINT
                            + "/"
                            + str(signalement)),
                           proxies=osmosecracker_config.OC_PROXIES,
                           auth=HTTPBasicAuth(
                                 osmosecracker_config.OC_ESPACECO_LOGIN,
                                 osmosecracker_config.OC_ESPACECO_PWD))
    except Exception as e:
        LOGGER.error(
                      "Erreur lors de la requête de récupération"
                      + "de statut du signalement.")
        raise Exception(e)
    else:
        if req.status_code == 200:
            return req.json()["status"]
        else:
            return None
