# ----------------------------------------------------------------------------
# Created By  : Nicolas py nicolas.py@ign.fr and Gabriel bregand gabriel.bregand@ign.fr
# Created Date: juillet 2024
# version ='1.1'
# ---------------------------------------------------------------------------
"""
Mise à jour d'OsmoseCracker pour réduire le nombre de signalements en créant des clusters de signalements.

Fichiers et fonctions modifiés
------------------------------
- osmosecracker.py : 
    - main (Signalements EspaceCollaboratif)
- osmosecracker_query_bduni.py : 
    - NEW clustering
- osmosecracker_espacecollaboratifign.py : 
    - post_signalement
- osmosecracker_issue.py :
    - class OsmoseCrackerIssue
    - __init__
-	osmosecracker_database_management :
    - create
    - insert


Note
----


"""
# ---------------------------------------------------------------------------

##########  osmosecracker.py    ##########
"""
Nos modifications ont lieu lors de l'émission des Signalements EspaceCollaboratif.

Nous utilisons la variable issuesSignalement.
    issuesSignalement est une liste d'objets de type classe
    composée des objets de la base de données OSMOSECRACKER
    qui ne sont pas dans une ZICAD et espacecosignalements = None.

Les clusters sont donc faits sur les nouveaux objets
et sur les objets qui n'ont pas de signalement (reprise sur incident).


"""

#####
# Signalements EspaceCollaboratif
#####
"""
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
"""

issuesSignalement_cluster: list(osmosecracker_issue.OsmoseCrackerIssue) = osmosecracker_query_bduni.clustering(issuesSignalement)


# ---------------------------------------------------------------------------

##########  osmosecracker_issue.py  ########## 
"""
Nouveaux objet de la class issue pour
stocké de maniere temporaire les 
information du clusteur 
(non persister en base)
"""
####
# création de la class
####

""" [...] """

"""
bduni_zicad: bool = field(
        init=False, compare=False)"""
    """ Dans une ZICAD ou non

    Vérification que l'objet ne soit pas
    dans une ZICAD pour ne pas créer un
    signalement inutile"""

# FROM 'clustering'
cluster_id: str = field(
        init=False, compare=False)
    """  id global du cluster
     concatenation 
        core_item_id
        core_class_id
        bduni_objet_attribut_1
        raw_cluster_id (num cluster) """

sketchcontent: str = field(
        init=False, compare=False)
    """ descriptif du cluster (geometrie) 
    selon le format sketch de l espace co """

""" [...] """

####
# def du init
####

""" [...] """

    self.cluster_id = None
    self.sketchcontent = None


# ---------------------------------------------------------------------------

##########  osmosecracker_query_bduni.py    ##########
"""
Fonction pour créer les clusters en utilisant 
le serveur BDUNI.

Parameters
----------
json_issues : 'JSON' 
    core_id 'varchar(50)'
    core_lat 'float'
    core_lon 'float'
    bduni_objet_attribut_1 'text'
    core_item_id 'int'
    core_class_id 'int'

Returns
-------
issue_rows 'List'
    core_id
    core_lon
    core_lat
    cluster_id (NEW)
    bduni_objet_attribut_1
    core_class_id
    core_item_id
    bounding_box (NEW)
    bounding_center_lon (NEW)
    bounding_center_lat (NEW)

Note
----
L'objectif est d'utiliser le plus possible
le serveur et de ne pas ajouter de bibliothèques
Python supplémentaires.


"""
#####
# Imports
#####
import json

""" [...] """

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
                -- Clustering
                WITH clusters AS (
                    SELECT 
                        core_id,
                        core_lat,
                        core_lon,
                        core_item_id, 
                        core_class_id,
                        bduni_objet_attribut_1,
                        -- Clustering spatial avec DBSCAN partitionné par les variables de l'objet
                        ST_ClusterDBSCAN(ST_SetSRID(ST_MakePoint(core_lon, core_lat), 4326), 0.0129711387703627, 2)
                        OVER (PARTITION BY core_item_id, core_class_id, bduni_objet_attribut_1) AS raw_cluster_id,
                        ST_SetSRID(ST_MakePoint(core_lon, core_lat), 4326) AS geom
                    FROM 
                        json_to_recordset(%s) AS x(
                            core_id varchar(50),
                            core_lat float,
                            core_lon float,
                            bduni_objet_attribut_1 text,
                            core_item_id int,
                            core_class_id int
                        )
                    ), 
                    -- Attribution d'identifiants uniques aux clusters
                    clusters_with_unique_ids AS (
                        SELECT 
                            clusters.*,
                            CASE WHEN raw_cluster_id IS NOT NULL 
                                THEN CONCAT(core_item_id, core_class_id, bduni_objet_attribut_1, raw_cluster_id) 
                                ELSE NULL 
                            END AS cluster_id
                        FROM 
                            clusters
                    ),
                    -- Création des bounding boxes et calcul du centre
                    cluster_bounding_boxes AS (
                        SELECT 
                            cluster_id,
                            ST_AsText(ST_Envelope(ST_Collect(geom))) AS bounding_box,
                            ST_X(ST_Centroid(ST_Extent(geom))) AS bounding_center_lon, -- Longitude du centre de la bounding box
                            ST_Y(ST_Centroid(ST_Extent(geom))) AS bounding_center_lat  -- Latitude du centre de la bounding box
                        FROM 
                            clusters_with_unique_ids
                        GROUP BY 
                            cluster_id
                        )
                -- Sélection finale avec jointure sur les clusters et les bounding boxes
                SELECT 
                    cl.core_id,
                    cl.core_lon,
                    cl.core_lat,
                    cl.cluster_id,
                    cl.bduni_objet_attribut_1,
                    cl.core_class_id,
                    cl.core_item_id,
                    cb.bounding_box,
                    cb.bounding_center_lon,
                    cb.bounding_center_lat
                FROM 
                    clusters_with_unique_ids AS cl
                LEFT JOIN 
                    cluster_bounding_boxes AS cb 
                ON 
                    cb.cluster_id = cl.cluster_id 
                ORDER BY 
                    cl.cluster_id,
                    ST_Distance(
                        ST_SetSRID(ST_MakePoint(cl.core_lon, cl.core_lat), 4326),
                        ST_SetSRID(ST_MakePoint(cb.bounding_center_lon, cb.bounding_center_lat), 4326)
                    ); -- Tri des clusters par identifiant de
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


# ---------------------------------------------------------------------------
##########  osmosecracker_espacecollaboratifign.py  ########## 
"""
fonction:
post_signalement  

Ajout :
sketchcontent (string): JSON contenant un croquis
+ x,y du zoom sur le croquis

"""

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


# ---------------------------------------------------------------------------

##########  osmosecracker.py    ##########
"""
Différentiation de l'emition des signalement
entre les cluster et les signalement normaux

la list des "issues_cluster" est en ordre croissant
des id cluster donc voici le fonctionnement :

Si l'id cluster est différent du préssedant et de None:
    On emet un signalement du cluster
    On stock signalementid

Sinon si l'id cluster a deja fait l'object d'un signalement:
    On transforme l'id du signalement 
    du cluster en -signalementid
    pour savoir quelle objet apartien à
    quelle cluster

Sinon il n'y a pas d'id cluster :
    On emet un signalement normal
    On stock signalementid

    
Dans tous les cas:
    On sauvegarde signalementid dans
    l'oject obj_select
"""


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
                            +"**Attention : ce signalement englobe une zone. Vous pouvez trouver cette zone sur la géométrie affichée ci-contre.**"
                            +"\n ",
                            theme=issue.espaceco_theme,
                            type_signalement=args.type_signalement,
                            sketchcontent=issue.sketchcontent)
                LOGGER.info("Un cluster a etait crée")
            else:
                 # signalement dans un clusteur qui a deja fait l'objet d'un signalement
                 signalementid = -abs(signalementid)
        else:
            #Traitement pour un signalement classique sans cluster
            reportcounter += 1
            signalementid = osmosecracker_espacecollaboratifign.post_signalement(
                            lon=issue.core_lon,
                            lat=issue.core_lat,
                            message=issue.details_descriptionstr,
                            theme=issue.espaceco_theme,
                            type_signalement=args.type_signalement)
        if signalementid is not None:
                        issue.espaceco_signalement_id = signalementid
                        issue.espaceco_signalement_status_refresh_timestamp = issuesSignalementTimestamp
                        issue.espaceco_signalement_status = args.type_signalement
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


# ---------------------------------------------------------------------------

##########  osmosecracker_database_management.py    ##########
"""
Modif de la base SQL aussi pour retirer l'attribut unique de espaceco_signalement_id
dans le but de savoir quelle signalement vas avec quelle cluster

Si dans un cluster deja fait
    id signalment = id du premier signalement du cluster

Mais espaceco_signalement_id etait unique donc nous avons du le modifier
"""

espaceco_signalement_id INT,