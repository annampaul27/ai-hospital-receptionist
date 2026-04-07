from typing import Any, Dict, List, TypedDict
from langgraph.graph import START, StateGraph
from app.logger import logger
from app.services.supabase_client import SupabaseClient
from app.services.webhook import WebhookService

class ReceptionState(TypedDict, total=False):
    user_message: str
    patient_name: str
    patient_age: str
    patient_query: str
    ward: str
    next_prompt: str
    completed: bool
    webhook_sent: bool
    error: str
    history: List[Dict[str, str]]
    assistant_message: str

class ReceptionWorkflow:
    EMERGENCY_KEYWORDS = {
        'accident', 'severe', 'bleeding', 'fracture', 'unconscious', 'chest pain', 'trauma', 
        'dizzy', 'faint', 'heart attack', 'stroke', 'seizure', 'choking', 'burn', 'poison',
        'overdose', 'allergic reaction', 'difficulty breathing', 'collapse', 'emergency',
        'urgent', 'critical', 'life threatening', 'ambulance', 'paramedics'
    }
    
    MENTAL_HEALTH_KEYWORDS = {
        'stress', 'anxiety', 'depression', 'panic', 'suicidal', 'overwhelmed', 'mental', 
        'trauma', 'therapy', 'counseling', 'psychiatric', 'psychological', 'mood', 
        'behavior', 'emotional', 'crisis', 'ptsd', 'bipolar', 'schizophrenia', 'addiction'
    }
    
    CARDIOLOGY_KEYWORDS = {
        'heart', 'chest pain', 'cardiac', 'blood pressure', 'hypertension', 'arrhythmia',
        'palpitations', 'angina', 'heart attack', 'myocardial', 'cardiovascular', 'ecg',
        'ekg', 'pacemaker', 'valve', 'coronary', 'atherosclerosis'
    }
    
    ORTHOPEDICS_KEYWORDS = {
        'bone', 'fracture', 'broken', 'sprain', 'strain', 'joint', 'arthritis', 'back pain',
        'neck pain', 'shoulder', 'knee', 'hip', 'spine', 'disc', 'herniated', 'surgery',
        'cast', 'brace', 'physical therapy', 'orthopedic'
    }
    
    PEDIATRICS_KEYWORDS = {
        'child', 'baby', 'infant', 'pediatric', 'newborn', 'toddler', 'teenager', 'growth',
        'development', 'vaccination', 'fever', 'rash', 'cough', 'ear infection', 'asthma'
    }

    def __init__(self, supabase_client: SupabaseClient, webhook_service: WebhookService) -> None:
        self.supabase_client = supabase_client
        self.webhook_service = webhook_service
        self.graph = StateGraph(ReceptionState)
        self.graph.add_node('process_input', self.process_input)
        self.graph.add_node('classify_ward', self.classify_ward)
        self.graph.add_node('clarify_missing', self.clarify_missing)
        self.graph.add_node('completion_check', self.completion_check)
        self.graph.add_node('trigger_webhook', self.trigger_webhook)
        self.graph.add_edge(START, 'process_input')
        self.graph.add_edge('process_input', 'classify_ward')
        self.graph.add_edge('classify_ward', 'clarify_missing')
        self.graph.add_edge('clarify_missing', 'completion_check')
        self.graph.add_edge('completion_check', 'trigger_webhook')
        self.compiled_graph = self.graph.compile()

    def run(self, state: ReceptionState) -> ReceptionState:
        logger.info('Running LangGraph workflow with current state: %s', {k: v for k, v in state.items() if k != 'history'})
        state.setdefault('history', [])
        state.setdefault('completed', False)
        state.setdefault('webhook_sent', False)
        state.setdefault('assistant_message', '')
        next_state = self.compiled_graph.invoke(state)
        logger.info('Workflow completed; completed=%s, webhook_sent=%s', next_state.get('completed'), next_state.get('webhook_sent'))
        return next_state

    def process_input(self, state: ReceptionState) -> ReceptionState:
        user_message = state.get('user_message', '').strip()
        if user_message:
            state['history'].append({'role': 'user', 'text': user_message})
        if not state.get('next_prompt'):
            state['next_prompt'] = 'ask_name'
            state['assistant_message'] = (
                'Hello and welcome to the hospital reception assistant. ' 
                'To get started, may I please have your full name?'
            )
            state['last_action'] = 'ask_name'
            return state

        if state.get('next_prompt') == 'ask_name' and user_message:
            if self._is_valid_name(user_message):
                state['patient_name'] = user_message
            else:
                state['error'] = 'Please provide your name so we can continue.'
                state['assistant_message'] = state['error']
                return state

        if state.get('next_prompt') == 'ask_age' and user_message:
            age = self._extract_age(user_message)
            if age:
                state['patient_age'] = age
            else:
                state['error'] = 'Age must be numeric. Please enter your age in years.'
                state['assistant_message'] = state['error']
                return state

        if state.get('next_prompt') == 'ask_query' and user_message:
            state['patient_query'] = user_message

        state['assistant_message'] = ''
        return state

    def classify_ward(self, state: ReceptionState) -> ReceptionState:
        if state.get('patient_query') and not state.get('ward'):
            query_text = state['patient_query'].lower()
            
            # Count keyword matches for each category
            score_emergency = sum(1 for kw in self.EMERGENCY_KEYWORDS if kw in query_text)
            score_mental = sum(1 for kw in self.MENTAL_HEALTH_KEYWORDS if kw in query_text)
            score_cardiology = sum(1 for kw in self.CARDIOLOGY_KEYWORDS if kw in query_text)
            score_orthopedics = sum(1 for kw in self.ORTHOPEDICS_KEYWORDS if kw in query_text)
            score_pediatrics = sum(1 for kw in self.PEDIATRICS_KEYWORDS if kw in query_text)
            
            # Determine ward based on highest score, with priority for emergency
            scores = {
                'Emergency Ward': score_emergency,
                'Mental Health Ward': score_mental,
                'Cardiology Ward': score_cardiology,
                'Orthopedics Ward': score_orthopedics,
                'Pediatrics Ward': score_pediatrics
            }
            
            # Emergency takes priority if any emergency keywords found
            if score_emergency >= 1:
                state['ward'] = 'Emergency Ward'
            else:
                # Find ward with highest non-zero score
                max_score = max(scores.values())
                if max_score >= 1:
                    # Get ward with highest score (excluding emergency)
                    best_ward = max(
                        [(ward, score) for ward, score in scores.items() if ward != 'Emergency Ward'],
                        key=lambda x: x[1]
                    )[0]
                    state['ward'] = best_ward
                else:
                    state['ward'] = 'General Ward'
            
            logger.info('Ward classification determined: %s for query=%s (scores: %s)', 
                       state['ward'], state['patient_query'], scores)
        return state

    def clarify_missing(self, state: ReceptionState) -> ReceptionState:
        if state.get('completed'):
            return state

        if not state.get('patient_name'):
            state['next_prompt'] = 'ask_name'
            state['assistant_message'] = 'Please tell me your full name so that I can begin registration.'
            return state

        if not state.get('patient_age'):
            state['next_prompt'] = 'ask_age'
            state['assistant_message'] = f'Thanks {state.get("patient_name")}. What is your age?'
            return state

        if not state.get('patient_query'):
            state['next_prompt'] = 'ask_query'
            state['assistant_message'] = (
                'Can you describe your current symptoms or reason for visiting the hospital today?'
            )
            return state

        if state.get('ward') and state.get('patient_name') and state.get('patient_age') and state.get('patient_query'):
            state['assistant_message'] = (
                'Thank you. I have enough information and I am routing you to the appropriate ward now.'
            )
            return state

        state['assistant_message'] = 'I am reviewing your information. One moment please.'
        return state

    def completion_check(self, state: ReceptionState) -> ReceptionState:
        if state.get('patient_name') and state.get('patient_age') and state.get('patient_query') and state.get('ward'):
            state['completed'] = True
        return state

    def trigger_webhook(self, state: ReceptionState) -> ReceptionState:
        if not state.get('completed') or state.get('webhook_sent'):
            return state

        try:
            record = self.supabase_client.store_patient_record(
                patient_name=state['patient_name'],
                patient_age=state['patient_age'],
                patient_query=state['patient_query'],
                ward=state['ward'],
            )
            payload = {
                'patient_name': record['patient_name'],
                'patient_age': str(record['patient_age']),
                'patient_query': record['patient_query'],
                'ward': record['ward'],
                'timestamp': record['timestamp'],
            }
            self.webhook_service.trigger_webhook(payload)
            state['webhook_sent'] = True
            state['completion_timestamp'] = record['timestamp']
            state['assistant_message'] = (
                f"Thank you, {state['patient_name']}. Your registration is complete. "
                f"I have classified you for the {state['ward']}. A clinician will be with you shortly."
            )
        except Exception as exc:
            logger.exception('Workflow webhook or storage failed')
            state['error'] = 'There was a technical issue sending your registration. Please try again in a moment.'
            state['assistant_message'] = state['error']
        return state

    def _is_valid_name(self, text: str) -> bool:
        return bool(text and len(text.strip()) > 2 and not any(char.isdigit() for char in text))

    def _extract_age(self, text: str) -> str:
        digits = ''.join([ch for ch in text if ch.isdigit()])
        return digits if digits and 1 <= len(digits) <= 3 else ''
