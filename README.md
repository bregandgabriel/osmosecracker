# OSMOSECRACKER

OSMOSE ([Wiki](https://wiki.openstreetmap.org/wiki/Osmose/api/0.3), [API](https://osmose.openstreetmap.fr/api/0.3/)) compare les données de l'IGN et d'OSM, créant ainsi des signalements destinés aux utilisateurs OSM, en comparant notre base de données à la leur.

[Vidéo de présentation d&#39;osmose url](https://peertube.openstreetmap.fr/w/aytqnoBJgNdPBEgvnFcViS)

> *"Osmose-QA est un outil de signalement d’anomalies dans les données d’OSM, mais également d’enrichissement d’OSM par la détection de manques d’objets ou de tags à partir de données compatibles en OpenData. Symétriquement, on peut aussi le voir comme un moyen d'enrichir l’OpenData grâce à OSM. Parallèlement aux signalements visibles sur l’interface d’Osmose-QA, des exports complets et enrichis des données OSM avec l’OpenData sont également redistribués. Globalement, l’idée est de généraliser le concept de BANO à d’autres jeux de données."*

— Frédéric Rodrigo (Développeur du Projet OSMOSE)

Lorsque les utilisateurs OSM privilégient la donnée OSM sur ces incohérences IGN-OSM, c'est peut être que la données IGN est perfectible.

OsmoseCracker permet de transtyper ces incohérences IGN-OSM jugées OSM-exacte par un contributeur OSM en signalements Espace collaboratif.

## Description

* [docs](docs)
  * [doc_utilisateur](docs/doc_utilisateur)
    * [20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.docx](docs/doc_utilisateur/20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.docx)*Word explique le fonctionnement et la manière de lancer OSMOSECRACKER à visée DATAC*
    * [20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.pdf](docs/doc_utilisateur/20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.pdf)*PDF explique le fonctionnement et la manière de lancer OSMOSECRACKER à visée DATAC*
    * [20240115-FichesProcessus-DATAC-MAJEC.docx](docs/doc_utilisateur/20240115-FichesProcessus-DATAC-MAJEC.docx)*Word explique le fonctionnement et la manière de traiter les signalements visée MAJEC*
    * [20240115-FichesProcessus-DATAC-MAJEC.pdf](docs/doc_utilisateur/20240115-FichesProcessus-DATAC-MAJEC.pdf)*PDF explique le fonctionnement et la manière de traiter les signalements visée MAJEC*
    * [20241021-doc_utilisateur.docx](docs/doc_utilisateur/20241021-doc_utilisateur.docx)*Word complémentaire de FichesProcessus-DATAC-DocLogicielTâchesDatac pour connaître tous les paramètres de lancement d'OSMOSECRACKER*
    * [20241021-doc_utilisateur.pdf](docs/doc_utilisateur/20241021-doc_utilisateur.pdf)*PDF complémentaire de FichesProcessus-DATAC-DocLogicielTâchesDatac pour connaître tous les paramètres de lancement d'OSMOSECRACKER*
    * [procédure_d_instalation_de_bibliothéque.pdf](docs/doc_utilisateur/procédure_d_instalation_de_bibliothéque.pdf)
      *PDF installation avec PROXY d'une bibliothèque python*
  * [rapports_mensuels](docs/rapports_mensuels)
    * [analyse_mensuelle_a2023m11.pdf](docs/rapports_mensuels/analyse_mensuelle_a2023m11.pdf)*Rapport de performance d'OSMOSECRACKER de novembre 2023*
    * [analyse_mensuelle_a2023m12.pdf](docs/rapports_mensuels/analyse_mensuelle_a2023m12.pdf)*Rapport de performance d'OSMOSECRACKER de decembre 2023*
    * [analyse_mensuelle_a2024m01.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m01.pdf)*Rapport de performance d'OSMOSECRACKER de janvier 2024*
    * [analyse_mensuelle_a2024m02.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m02.pdf)*Rapport de performance d'OSMOSECRACKER de février 2024*
    * [analyse_mensuelle_a2024m03.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m03.pdf)*Rapport de performance d'OSMOSECRACKER de mars 2024*
    * [analyse_mensuelle_a2024m04.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m04.pdf)*Rapport de performance d'OSMOSECRACKER de avril 2024*
    * [analyse_mensuelle_a2024m05.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m05.pdf)*Rapport de performance d'OSMOSECRACKER de mai 2024*
    * [analyse_mensuelle_a2024m06.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m06.pdf)*Rapport de performance d'OSMOSECRACKER de juin 2024*
    * [analyse_mensuelle_a2024m07.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m07.pdf)*Rapport de performance d'OSMOSECRACKER de juillet 2024*
    * [analyse_mensuelle_a2024m08-09.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m08-09.pdf)*Rapport de performance d'OSMOSECRACKER de août et septembre 2024*
    * [analyse_mensuelle_a2024m10.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m10.pdf)*Rapport de performance d'OSMOSECRACKER de octobre 2024*
    * [analyse_mensuelle_a2024m11.pdf](docs/rapports_mensuels/analyse_mensuelle_a2024m11.pdf)*Rapport de performance d'OSMOSECRACKER de november 2024*
    * [Rapport_OSMOSECRACKER_Annuel_2024.pdf](docs/rapports_mensuels/Rapport_OSMOSECRACKER_Annuel_2024.pdf)*Rapport de performance Annuel d'OSMOSECRACKER de 2024*
    * [20240319_graphique_osmosecracker.xlsx](docs/rapports_mensuels/20240319_graphique_osmosecracker.xlsx)
      *Excel utilisé pour tous les graphiques des rapports d'OSMOSECRACKER*
  * [57_Re_diffusion_d_OpenData_enrichie_par_Osmose_QA_480p_hls.mp4](docs/57_Re_diffusion_d_OpenData_enrichie_par_Osmose_QA_480p_hls.mp4)*Presentation par Frédéric Rodrigo d'osmose*
  * [20231006_presentation_du_projet_osmosecracker.mp4](docs/20231006_presentation_du_projet_osmosecracker.mp4)*Presentation vidéo d'OSMOSECRACKER*
  * [20231030_resultat_osmosecracker.pptx](docs/20231030_resultat_osmosecracker.pptx)*Power Point des premiers résultats d'OSMOSECRACKER utilisé pour la présentation vidéo*
  * [20231107_schema_osmosecracker.pdf](docs/20231107_schema_osmosecracker.pdf)
    *Schéma de fonctionnement d'OSMOSECRACKER*
* [src](src)
  * [osmosecracker.py](src/osmosecracker.py)
  * [osmosecracker_config.py](src/osmosecracker_config.py)
  * [osmosecracker_exceptions.py](src/osmosecracker_exceptions.py)
  * [osmosecracker_workflow.py](src/osmosecracker_workflow.py)
  * [osmosecracker_query_osm.py](src/osmosecracker_query_osm.py)
  * [osmosecracker_query_osmose.py](src/osmosecracker_query_osmose.py)
  * [osmosecracker_espacecollaboratifign.py](src/osmosecracker_espacecollaboratifign.py)
  * [osmosecracker_query_bduni.py](src/osmosecracker_query_bduni.py)
  * [osmosecracker_issue.py](src/osmosecracker_issue.py)
  * [osmosecracker_database.sqlite](src/osmosecracker_database.sqlite)
  * [osmosecracker_database_management.py](src/osmosecracker_database_management.py)

*Pour plus d'informations sur le src lire* ***"INFRASTRUCTURE LOGICIEL DE REFERENCE ET GRANDES LIGNES DU DEVELOPPEMENT"*** *dans* [*20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.pdf*](docs/doc_utilisateur/20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.pdf)

## Getting Started

### Dependencies

* libraries python :

*Bibliothèques incluses dans la bibliothèque standard de Python (pas besoin d'installation supplémentaire) :*

```
__future__
argparse
dataclasses
datetime
json
logging
math
os
pathlib
sqlite3
sys
typing
urllib.parse
uuid
```

*Bibliothèques nécessitant une installation supplémentaire :*

```
dataclass_csv
psycopg2
psycopg2.extras
requests
requests.auth
urllib3
```

### Installing

* Récupérer le script dans [src](src) **/!\ il faut tout le programme /!\\**
* Installer toutes les libraries python
  *(si vous ne savez pas comment faire suivre les étapes dans [procédure_d&#39;installation_de_bibliothèque.pdf](docs/doc_utilisateur/procédure_d_instalation_de_bibliothéque.pdf))*

### Executing program

Comment lancer le programme:

```
emplacement_du_script/osmosecracker.py -ts "signalements de l'espace CO sont émis ou non" -fdep "departements"
```

Exemple :

**/!\ Ne pas lancer sens avoir pris connaissance de la documentation /!\\**

```
src/osmosecracker.py -ts submit -fdep "34" "69"
```

**/!\ Il y a un grand nombres de parametre utilisateur et dévlopeur /!\\**
Pour plus d'informations sur les paramètres utilisateur et les paramètres dévlopeur lire : [20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.pdf](docs/doc_utilisateur/20240115-FichesProcessus-DATAC-DocLogicielTâchesDatac.pdf)

## Authors

[Nicolas PY](nicolas.py@ign.fr)

[Gabriel BREGAND](gabriel.bregand@gmail.com)
