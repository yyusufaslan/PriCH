
import sys
import os
import traceback
import importlib.util

try:
    import spacy
    from collections import defaultdict
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("spaCy not available - AI features will be disabled")

class SpacyChecker:
    def __init__(self):
        self.nlp = None
        self.nlp_models = {}
        self.custom_terms = {}
        
        # Try to load default model if spaCy is available
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("Successfully loaded spaCy model: en_core_web_sm")
            except OSError:
                print("spaCy model 'en_core_web_sm' not found. AI features will be disabled.")
                print("To enable AI features, run: python -m spacy download en_core_web_sm")
            except Exception as e:
                print(f"Error loading spaCy model: {e}")

    def is_model_installed(self, model_name: str) -> bool:
        """Return True if the spaCy pipeline is installed in current env."""
        if not SPACY_AVAILABLE:
            return False
        try:
            import spacy.cli
            info = spacy.cli.info()
            pipelines = set((info or {}).get("pipelines", {}).keys())
            return model_name in pipelines
        except Exception:
            # Fallback: attempt to import package
            try:
                __import__(model_name)
                return True
            except Exception:
                return False

    def download_spacy_model(self, model_name):
        if not SPACY_AVAILABLE:
            print("SpaCy is not available. Cannot download model.")
            return False

        import subprocess
        try:
            print(f"Downloading spaCy model: {model_name}")
            print(f"Using Python: {sys.executable}")

            # Skip if already installed
            if self.is_model_installed(model_name):
                print(f"spaCy model '{model_name}' already installed. Skipping download.")
                return True

            # Prefer spaCy CLI API first
            try:
                import spacy.cli
                # Attempt download via spaCy's Python API (avoids shelling to pip directly)
                try:
                    spacy.cli.download(model_name)
                except BaseException as be:  # catch SystemExit from spaCy CLI
                    raise RuntimeError(f"spaCy CLI download aborted: {be}")
                print(f"Downloaded spaCy model: {model_name} successfully (via spacy.cli).")
                return True
            except Exception as cli_err:
                print(f"spaCy CLI download failed or not available: {cli_err}")
                # Fall through to subprocess methods

            # Ensure pip is available in this interpreter (fixes 'No module named pip')
            if importlib.util.find_spec('pip') is None:
                try:
                    print("Bootstrapping pip via ensurepip...")
                    subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
                except Exception as ensure_err:
                    print(f"Failed to bootstrap pip: {ensure_err}")

            # Retry download using 'python -m spacy download ...'
            result = subprocess.run([sys.executable, "-m", "spacy", "download", model_name], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Downloaded spaCy model: {model_name} successfully (via subprocess).")
                return True
            else:
                print("spaCy download subprocess failed.")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")

            # Final fallback: try installing the pip package directly (models are pip packages)
            try:
                pkg_name = model_name
                print(f"Attempting direct pip install of model package: {pkg_name}")
                subprocess.run([sys.executable, "-m", "pip", "install", pkg_name], check=True)
                return True
            except Exception as pip_err:
                print(f"Direct pip install failed: {pip_err}")

            return False
        except Exception as e:
            print(f"Error downloading spaCy model {model_name}: {str(e)}")
            traceback.print_exc()
            return False

    def uninstall_spacy_model(self, model_name):
        """Remove a spaCy model package from the current environment.
        Uses pip uninstall if available; attempts to bootstrap pip if missing.
        """
        if not model_name:
            print("No model name provided to uninstall.")
            return False

        import subprocess
        try:
            print(f"Uninstalling spaCy model: {model_name}")
            # Ensure pip exists
            if importlib.util.find_spec('pip') is None:
                try:
                    print("Bootstrapping pip via ensurepip for uninstall...")
                    subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
                except Exception as ensure_err:
                    print(f"Failed to bootstrap pip: {ensure_err}")
            # Uninstall non-interactively
            result = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", model_name], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Uninstalled spaCy model: {model_name}")
                return True
            print("pip uninstall failed.")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
        except Exception as e:
            print(f"Error uninstalling spaCy model {model_name}: {e}")
            traceback.print_exc()
            return False

    def load_spacy_model(self, model_name):
        if not SPACY_AVAILABLE:
            print("SpaCy is not available. Cannot load model.")
            return False
            
        try:
            self.nlp = spacy.load(model_name)
            print(f"Loaded spaCy model: {model_name} successfully.")
            return True
        except OSError as e:
            print(f"Error loading spaCy model {model_name}: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error loading model {model_name}: {str(e)}")
            traceback.print_exc()
            return False
        
    def load_spacy_models(self, model_names):
        if not SPACY_AVAILABLE:
            print("SpaCy is not available. Cannot load models.")
            return False
            
        try:
            print(f"Attempting to load spaCy models: {model_names}")
            
            # Handle both list and single string inputs
            if isinstance(model_names, str):
                model_names = [model_names]
            
            if not model_names:
                print("No models provided to load")
                return False
                
            # Clear existing models and load new ones
            self.nlp_models = {}
            
            for model_name in model_names:
                try:
                    self.nlp_models[model_name] = spacy.load(model_name)
                    print(f"Successfully loaded: {model_name}")
                except Exception as e:
                    print(f"Error loading model {model_name}: {str(e)}")
                    # Continue loading other models even if one fails
            
            if not self.nlp_models:
                print("Failed to load any models")
                return False
                
            print(f"Successfully loaded {len(self.nlp_models)} spaCy models")
            return True
        except Exception as e:
            print(f"Error in load_spacy_models: {str(e)}")
            traceback.print_exc()
            return False

    def analyze_and_replace_entities(self, text):
        if not SPACY_AVAILABLE:
            print("SpaCy is not available. Cannot analyze text.")
            return {}
            
        if not self.nlp_models and not self.nlp:
            print("No models loaded. Cannot analyze text.")
            return {}
            
        replacements = {}
        
        try:
            # Use single model if available
            if self.nlp:
                return self._analyze_with_model(self.nlp, text)
            
            # Use multiple models if available
            if self.nlp_models:
                for lang, nlp in self.nlp_models.items():
                    try:
                        model_replacements = self._analyze_with_model(nlp, text)
                        replacements.update(model_replacements)
                    except Exception as e:
                        print(f"Error processing with model {lang}: {str(e)}")
                        # Continue with other models even if one fails
            
            return replacements
            
        except Exception as e:
            error_msg = f"Error in analyze_and_replace_entities: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return {} # Return empty dict on error

    def _analyze_with_model(self, nlp, text):
        """Helper method to analyze text with a single spaCy model"""
        replacements = {}
        
        try:
            # Process the text with spaCy
            doc = nlp(text)
            
            # Keep track of entity counts for numbering
            entity_counts = defaultdict(int)
            
            # Custom terms processing
            for token in doc:
                token_lower = token.text.lower()  # Convert to lowercase for normalization
                if token_lower in self.custom_terms:
                    if token.text not in replacements:
                        replacements[token.text] = self.custom_terms[token_lower]
            
            # First pass: count entities and create replacements
            for ent in doc.ents:
                entity_counts[ent.label_] += 1
                replacement = f"{ent.label_}{entity_counts[ent.label_]}"
                if ent.text not in replacements:
                    replacements[ent.text] = replacement
            
            return replacements
            
        except Exception as e:
            print(f"Error in _analyze_with_model: {str(e)}")
            return {}

    def set_custom_terms(self, terms_map):
        try:
            self.custom_terms = terms_map
            print(f"Set {len(self.custom_terms)} custom terms")
            return True
        except Exception as e:
            print(f"Error setting custom terms: {str(e)}")
            return False

    def get_downloaded_spacy_models(self):
        """Get a list of downloaded spaCy models as a JSON string."""
        import subprocess
        import json
        
        try:
            # First check if spaCy is installed
            if not SPACY_AVAILABLE:
                print("SpaCy is not available. Cannot get downloaded models.")
                return json.dumps({"error": "spaCy not available", "models": []})
            
            # Try to get installed models directly from spaCy
            try:
                import spacy.cli
                #print("Using spaCy directly to get model info")
                installed_models = list(spacy.cli.info()["pipelines"].keys())
                return json.dumps({"models": installed_models})
            except Exception as e:
                print(f"Error getting models directly from spaCy: {str(e)}")
                print("Falling back to subprocess method")
            
            # Fall back to subprocess method
            try:
                print(f"Using subprocess to run: {sys.executable} -m spacy info --json")
                result = subprocess.run(
                    [sys.executable, "-m", "spacy", "info", "--json"], 
                    capture_output=True, 
                    text=True,
                    timeout=10  # Add timeout to prevent hanging
                )
                
                # Check if command was successful
                if result.returncode != 0:
                    print(f"Command failed with code {result.returncode}")
                    print(f"Error output: {result.stderr}")
                    # Return empty list with error info
                    return json.dumps({"error": result.stderr, "models": []})
                
                # Try to parse output as JSON
                try:
                    info = json.loads(result.stdout)
                    if "pipelines" in info:
                        models = list(info["pipelines"].keys())
                        print(f"Found {len(models)} models: {models}")
                        return json.dumps({"models": models})
                    else:
                        print("No pipelines found in spaCy info output")
                        return json.dumps({"error": "No pipelines in output", "models": []})
                except json.JSONDecodeError:
                    print(f"Invalid JSON from spaCy info: {result.stdout}")
                    return json.dumps({"error": "Invalid JSON from spaCy", "models": []})
                    
            except subprocess.TimeoutExpired:
                print("Command timed out after 10 seconds")
                return json.dumps({"error": "Command timed out", "models": []})
            except Exception as e:
                print(f"Subprocess error: {str(e)}")
                return json.dumps({"error": str(e), "models": []})
                
        except Exception as e:
            print(f"Error getting downloaded spaCy models: {str(e)}")
            traceback.print_exc()
            return json.dumps({"error": str(e), "models": []})