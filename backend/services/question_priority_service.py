"""
Question Priority Service for SamvaadAI.

Provides field value simulation capabilities for the Adaptive Questioning Engine.
Maintains deterministic field value sets for consistent simulation results.

Architectural Guarantees:
- Deterministic field value sampling
- Performance-optimized value sets (max 10 values per field)
- No external dependencies
- Thread-safe operations
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Maximum simulations per field for performance
MAX_FIELD_SIMULATIONS = 10

# Deterministic field value sets for simulation
# These represent the most common/impactful values for each field
FIELD_VALUE_SETS = {
    "state": [
        "Maharashtra", "Karnataka", "Uttar Pradesh", "Tamil Nadu", 
        "Gujarat", "Rajasthan", "West Bengal", "Madhya Pradesh",
        "Andhra Pradesh", "Telangana"
    ],
    "income_range": [
        "below_1l", "1l_to_2l", "2l_to_5l", "5l_to_10l", "above_10l"
    ],
    "age_group": [
        "18-25", "26-35", "36-45", "46-60", "60+"
    ],
    "occupation": [
        "farmer", "student", "unemployed", "self_employed", 
        "private_employee", "government_employee", "labourer", "business"
    ],
    "gender": [
        "male", "female", "other"
    ],
    "caste_category": [
        "general", "obc", "sc", "st"
    ],
    "farmer_status": [
        "marginal", "small", "medium", "large", "landless"
    ],
    "student_status": [
        "school", "college", "postgraduate", "professional"
    ],
    "disability_status": [
        "none", "physical", "visual", "hearing", "multiple"
    ],
    "education_level": [
        "none", "primary", "secondary", "higher_secondary", "graduate", "postgraduate"
    ],
    "land_ownership": [
        "yes", "no", "leased"
    ],
    "employment_status": [
        "employed", "self_employed", "unemployed", "student", "retired"
    ],
    "urban_rural": [
        "urban", "rural"
    ],
    "bank_account": [
        True, False
    ],
    "bpl_status": [
        True, False
    ],
    "minority_status": [
        "none", "religious_minority", "linguistic_minority"
    ],
    "family_size": [
        1, 2, 3, 4, 5, 6, 7, 8
    ]
}

# Question text mapping for deterministic question generation
QUESTION_TEXTS = {
    "state": "Which state do you live in?",
    "income_range": "What is your approximate annual household income?",
    "age_group": "Which age group do you belong to?",
    "occupation": "What is your primary occupation?",
    "gender": "What is your gender?",
    "caste_category": "Which caste category do you belong to?",
    "farmer_status": "What type of farmer are you?",
    "student_status": "What is your current education level?",
    "disability_status": "Do you have any disability?",
    "education_level": "What is your highest education level?",
    "land_ownership": "Do you own agricultural land?",
    "employment_status": "What is your employment status?",
    "urban_rural": "Do you live in an urban or rural area?",
    "bank_account": "Do you have a bank account?",
    "bpl_status": "Do you have a BPL (Below Poverty Line) ration card?",
    "minority_status": "Do you belong to a minority community (for example Muslim, Christian, Sikh)?",
    "family_size": "How many members are in your family?"
}


class QuestionPriorityService:
    """
    Service for determining question priorities through field value simulation.
    
    Provides deterministic field value sets and simulation capabilities
    for the Adaptive Questioning Engine.
    """
    
    def __init__(self):
        """Initialize the question priority service."""
        self.field_values = FIELD_VALUE_SETS.copy()
        self.question_texts = QUESTION_TEXTS.copy()
        logger.info("QuestionPriorityService initialized")
    
    def get_simulation_values(self, field: str) -> List[Any]:
        """
        Get simulation values for a specific field.
        
        Args:
            field: The profile field name
            
        Returns:
            List of values to simulate for this field (max 10 values)
        """
        values = self.field_values.get(field, [])
        
        # Ensure we don't exceed MAX_FIELD_SIMULATIONS
        if len(values) > MAX_FIELD_SIMULATIONS:
            values = values[:MAX_FIELD_SIMULATIONS]
        
        logger.debug(f"Simulation values for {field}: {len(values)} values")
        return values
    
    def get_question_text(self, field: str) -> str:
        """
        Get deterministic question text for a field.
        
        Args:
            field: The profile field name
            
        Returns:
            Question text string
        """
        return self.question_texts.get(field, f"Please provide your {field}?")
    
    def get_all_simulatable_fields(self) -> List[str]:
        """
        Get list of all fields that can be simulated.
        
        Returns:
            List of field names that have simulation values
        """
        return sorted(list(self.field_values.keys()))
    
    def validate_field(self, field: str) -> bool:
        """
        Check if a field can be simulated.
        
        Args:
            field: The profile field name
            
        Returns:
            True if field has simulation values, False otherwise
        """
        return field in self.field_values