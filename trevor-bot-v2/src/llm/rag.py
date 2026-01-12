"""RAG (Retrieval-Augmented Generation) system for medical knowledge."""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from loguru import logger


class MedicalKnowledgeRAG:
    """RAG system for retrieving relevant medical knowledge."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize RAG system with ChromaDB."""
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="medical_knowledge",
            metadata={"description": "Sickle cell disease medical knowledge base"},
        )

        # Initialize embedding model (multilingual for French support)
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        logger.info("RAG system initialized")

    def add_document(
        self,
        content: str,
        metadata: Dict,
        doc_id: str,
    ):
        """
        Add a document to the knowledge base.

        Args:
            content: Document text content
            metadata: Document metadata (title, source, category, etc.)
            doc_id: Unique document identifier
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()

            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id],
            )

            logger.info(f"Added document to knowledge base: {doc_id}")

        except Exception as e:
            logger.error(f"Error adding document: {e}")

    def add_documents_batch(
        self,
        contents: List[str],
        metadatas: List[Dict],
        doc_ids: List[str],
    ):
        """
        Add multiple documents in batch.

        Args:
            contents: List of document texts
            metadatas: List of metadata dicts
            doc_ids: List of document IDs
        """
        try:
            # Generate embeddings in batch
            embeddings = self.embedding_model.encode(contents).tolist()

            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=doc_ids,
            )

            logger.info(f"Added {len(doc_ids)} documents to knowledge base")

        except Exception as e:
            logger.error(f"Error adding documents batch: {e}")

    def retrieve(
        self,
        query: str,
        n_results: int = 3,
        filter_metadata: Dict = None,
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User's question or message
            n_results: Number of documents to retrieve
            filter_metadata: Optional metadata filters (e.g., {"category": "crisis_management"})

        Returns:
            List of relevant documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
            )

            # Format results
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    retrieved_docs.append(
                        {
                            "content": doc,
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i]
                            if "distances" in results
                            else None,
                        }
                    )

            logger.info(f"Retrieved {len(retrieved_docs)} documents for query: {query[:50]}...")

            return retrieved_docs

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def format_retrieved_knowledge(self, documents: List[Dict]) -> str:
        """
        Format retrieved documents for LLM context.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted string for system prompt
        """
        if not documents:
            return ""

        formatted = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            title = metadata.get("title", f"Document {i}")
            source = metadata.get("source", "Unknown")
            content = doc.get("content", "")

            formatted.append(f"**Source {i}: {title}** (from {source})\n{content}\n")

        return "\n".join(formatted)

    def get_collection_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name,
        }


# Initialize medical knowledge with some basic documents
def initialize_knowledge_base(rag: MedicalKnowledgeRAG):
    """Populate knowledge base with initial medical documents."""

    initial_documents = [
        {
            "id": "hydration_importance",
            "content": """L'hydratation est cruciale pour les patients atteints de drépanocytose.

Recommandations:
- Boire 2-3 litres d'eau par jour (ajuster selon l'âge et le poids)
- Augmenter l'apport hydrique pendant l'exercice, la chaleur, ou en cas de fièvre
- Éviter l'alcool et limiter la caféine (effet diurétique)
- Surveiller la couleur de l'urine (doit être jaune pâle)

La déshydratation augmente le risque de crise vaso-occlusive car elle favorise la falciformation des globules rouges.""",
            "metadata": {
                "title": "Importance de l'hydratation",
                "source": "NIH Sickle Cell Disease Guidelines",
                "category": "prevention",
                "language": "fr",
            },
        },
        {
            "id": "crisis_management",
            "content": """Gestion de la crise vaso-occlusive:

**Signes d'une crise:**
- Douleur intense (os, articulations, abdomen, thorax)
- Fièvre
- Gonflement des mains/pieds

**Actions immédiates:**
1. Prendre les antalgiques prescrits (paracétamol, AINS si autorisé)
2. Boire beaucoup d'eau
3. Appliquer chaleur locale sur zones douloureuses
4. Se reposer

**Quand consulter en urgence:**
- Douleur thoracique
- Difficultés respiratoires
- Fièvre > 38.5°C
- Douleur non contrôlée par antalgiques habituels
- Priapisme > 2 heures

En cas de crise sévère, ne pas hésiter à se rendre aux urgences HUG.""",
            "metadata": {
                "title": "Gestion de la crise vaso-occlusive",
                "source": "HUG Hematology Protocol",
                "category": "crisis_management",
                "language": "fr",
            },
        },
        {
            "id": "hydroxyurea_benefits",
            "content": """L'hydroxyurée (Hydrea, Siklos) est le traitement de fond principal de la drépanocytose.

**Bénéfices:**
- Réduit la fréquence des crises douloureuses (jusqu'à 50%)
- Diminue les hospitalisations
- Réduit le risque de syndrome thoracique aigu
- Augmente l'hémoglobine fœtale (HbF) qui protège contre la falciformation

**Prise:**
- Une fois par jour, tous les jours
- À heure fixe pour optimiser l'efficacité
- Peut prendre 3-6 mois pour voir les effets complets

**Surveillance:**
- Prise de sang régulière (tous les 1-3 mois)
- Adaptation de dose selon numération
- Importance de ne JAMAIS arrêter sans avis médical

L'adhésion au traitement est essentielle pour son efficacité.""",
            "metadata": {
                "title": "Hydroxyurée: traitement de fond",
                "source": "Swiss Society of Hematology Guidelines",
                "category": "medication",
                "language": "fr",
            },
        },
        {
            "id": "infection_prevention",
            "content": """Les patients drépanocytaires ont un risque accru d'infections, notamment à pneumocoque.

**Prévention:**
- Vaccinations à jour (pneumocoque, grippe, méningocoque, COVID-19)
- Antibioprophylaxie (pénicilline) jusqu'à l'âge adulte
- Hygiène des mains rigoureuse
- Éviter contact avec personnes malades

**Signes d'infection nécessitant consultation urgente:**
- Fièvre ≥ 38.5°C
- Frissons
- Toux persistante
- Difficultés respiratoires
- Douleurs à la miction

Toute fièvre chez un patient drépanocytaire doit être considérée comme une urgence médicale.""",
            "metadata": {
                "title": "Prévention des infections",
                "source": "WHO Sickle Cell Disease Management",
                "category": "prevention",
                "language": "fr",
            },
        },
        {
            "id": "physical_activity",
            "content": """L'activité physique est bénéfique mais nécessite des précautions.

**Recommandations:**
- Privilégier les activités modérées et régulières
- Éviter les efforts intenses prolongés
- S'hydrater avant, pendant et après l'exercice
- Éviter les sports avec variations brutales de température
- Préférer les activités en endurance plutôt qu'en sprint

**Sports adaptés:**
- Marche, randonnée
- Natation (eau tempérée, pas froide)
- Vélo
- Yoga, pilates
- Danse modérée

**À éviter:**
- Plongée sous-marine
- Alpinisme en haute altitude
- Sports de combat intenses
- Entraînements épuisants

L'activité physique améliore la qualité de vie et le bien-être psychologique.""",
            "metadata": {
                "title": "Activité physique et drépanocytose",
                "source": "European Hematology Association Guidelines",
                "category": "lifestyle",
                "language": "fr",
            },
        },
    ]

    # Add initial documents
    for doc in initial_documents:
        rag.add_document(
            content=doc["content"],
            metadata=doc["metadata"],
            doc_id=doc["id"],
        )

    logger.info(f"Initialized knowledge base with {len(initial_documents)} documents")
