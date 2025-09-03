#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: avril 2023
# Modif Date : January 2024
# version ='1.1'
# ---------------------------------------------------------------------------
"""
Contient les paramètres de configuration de l'application Osmose Cracker :
- Les informations utiles pour nos appels API,
- Les informations du proxy,
- Les constantes de développeur,
- Des informations sur les objets que nous collectons,
- Les paramètres permettant de vérifier la connexion internet.

Note
----
Les paramètres ne doivent pas être modifiés, 
sauf en cas de modification importante des paramètres de développement.
"""
# ---------------------------------------------------------------------------

# https://docs.python.org/3/library/typing.html#typing.Final
# A special typing construct to indicate to type checkers that a name cannot be
# re-assigned or overridden in a subclass.
import logging
import os
from typing import Final
import osmosecracker_exceptions

LOGGER = logging.getLogger('OsmoseCracker.Config')

#####
# Connexion BDUni
#####

OC_BDUNI_HOST: Final[str] = "*********"
"""Connexion BDUni, database host address"""

OC_BDUNI_PORT: Final[int] = "*********"
"""Connexion BDUni *********"""

OC_BDUNI_DBNAME: Final[str] = "*********"
"""Connexion BDUni, the database name"""

OC_BDUNI_USER: Final[str] = "*********"
"""Connexion BDUni, database host address"""

if "OsmoseCracker_BDUNIConsultationInvite_PASSWORD" in "*********":
    OC_BDUNI_PASSWORD: Final[str] = "*********"
    """Connexion BDUni, database host address"""
else:
    raise "******************"('"*********":')


#####
# Connexion Espace Collaboratif
#####
if "OsmoseCracker_ESPACECO_LOGIN" in "*********":
    OC_ESPACECO_LOGIN: Final[str] = "*********"
    """Connexion Espace Collaboratif, Login du compte EspaceCo"""
else:
    raise "******************"('"*********":')

if "OsmoseCracker_ESPACECO_PASSWORD" in "*********":
    OC_ESPACECO_PWD: Final[str] = "*********"
    """Connexion Espace Collaboratif, Password du compte EspaceCo"""
else:
    raise "******************"('"*********":')

OC_ESPACECO_GROUPE:  Final[int] = "*********"
"""Connexion Espace Collaboratif, Groupe dans lequel faire le signalement"""
# "*********"
# "*********"

#####
# ______________________________________________________________________
#####

#####
# Constantes développeur WEB, ne pas modifier
#####

# Timeout et génériques
OC_TIMEOUT: Final[int] = 3
"""Constantes développeur WEB, Timeout en secondes"""

OC_HEADERS: Final[dict] = {"HTTP_HOST": "IGNF/osmosecracker/1.0",
                           "User-Agent": "IGNF/osmosecracker/1.0"}
"""Constantes développeur WEB, Headers user-agent du programme"""
# https://wikipython.flibuste.net/CodesReseau.html
# https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python

# Paramètres de proxy
OC_HTTPS_PROXY: Final[str] = "*********"
"""Constantes développeur WEB, The HTTPS proxy to use"""

OC_HTTP_PROXY: Final[str] = "*********"
"""Constantes développeur WEB, The HTTP proxy to use"""

OC_PROXIES = {
         'http': OC_HTTP_PROXY,
         'https': OC_HTTPS_PROXY
         }
""" La concaténation des 2 proxies pour nous permettre de faire
 des appels à des sites HTTP ou HTTPS. """

# URL à tester/pinger pour déterminer accès web
OC_WEBCONNEXION_URLs: Final[str] = ['https://www.google.com/']
"""Constantes développeur WEB, Les URLs des sites qui vérifieront si la connexion à Internet
 est possible ou non."""

#####
# Constantes développeur Osmose, ne pas modifier
#####

# EndPoint Omsose
OC_OSMOSE_ENDPOINT: Final[str] = "https://osmose.openstreetmap.fr/api/0.3/"
"""Constantes développeur Osmose, EndPoint Omsose """

OC_LIMIT: Final[int] = 10000
"""Constantes développeur Osmose, nombre d'objets maximum par ITEM/CLASSE que la requête renverra,
limite à 10 000 """

OC_FULL: Final[bool] = 'true'
"""Constantes développeur Osmose, si "full = false" quand le format JSON est demandée en sortie de l'api
cela ne revoie pas toute les information sur la données
mais que les plus importante. """

OC_WEBCONNEXION_URLs.append(OC_OSMOSE_ENDPOINT)
# On ajoute aux sites testés le site test de connexion au serveur OSMOSE.


#####
# Constantes développeur EspaceCollaboratif, ne pas modifier
#####

# EndPoint Espace Collaboratif
OC_ESPACECO_ENDPOINT:  Final[str] = "https://espacecollaboratif.ign.fr/gcms/api/reports"
"""Constantes développeur EspaceCollaboratif, EndPoint Espace Collaboratif """

OC_UNCLOSED_STATUSES: Final[str] = ["valid", "valid0", "reject", "reject0"]
"""Constantes développeur EspaceCollaboratif, Liste des status EspaceCo considérés comme non clos. """


#####
# Constantes développeur du programme, ne pas modifier
#####

# En tête de rapport/signalement
OC_REPORT_KEYWORD: Final[str] = "ROBOT_OSMOSECRACKER"
"""Constantes développeur du programme, en tête des signalements EspaceCo"""

OC_ITEM_INFO: Final = {7170:    {'name_en': "road",
                                 'name_fr': "route",
                                 'classe': {1: {'titre_fr':
                                                    " OSM ne constate pas de route à cet endroit, la route existante IGN est-elle présente ? ",
                                                'titre_en':
                                                    " possibly  missing  highway  in  the  area  (BD  Topo  IGN) "},
                                            3: {'titre_fr':
                                                    " OSM ne constate pas de route à cet endroit, la route existante IGN est-elle présente ? ",
                                                'titre_en':
                                                    " missing  ref=*  or  misaligned  road  compared  to  BDTopo  IGN "},
                                            4: {'titre_fr':
                                                    " OSM ne constate pas le même type de route que l'IGN ",
                                                'titre_en':
                                                    " Misaligned  road  compared  to  BDTopo  IGN  or  bad  highway=*  type "},
                                            13: {'titre_fr':
                                                    " OSM ne constate pas de route à cet endroit, la route existante IGN est-elle présente ? ",
                                                'titre_en':
                                                    " Road not integrated "},
                                            20: {'titre_fr':
                                                    "  OSM ne constate pas le même nombre de voies  ",
                                                 'titre_en':
                                                    " lanes=* missing  on  highway  with  more  than  2  lanes  (BD  Topo) "}},
                                 'theme_espace_co_ign': "Route",
                                 'classe_bduni': 'troncon_de_route',
                                 'attributs_bduni':
                                 {
                                    'attribut_1': 'nom_collaboratif_gauche',
                                    'attribut_2': 'nature',
                                    'attribut_3': 'nombre_de_voies',
                                    'attribut_4': 'importance',
                                    'attribut_5': 'importance',
                                    'attribut_geometrie': 'geometrie'
                                 }}}
"""Constantes développeur du programme, dictionnaire des tuple [items Osmose et leurs classes] considérés dans l'application."""
