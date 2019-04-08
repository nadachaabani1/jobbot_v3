# -*- coding: utf-8 -*-
from typing import Dict, Text, Any, List, Union

from rasa_core_sdk import ActionExecutionRejection
from rasa_core_sdk import Tracker
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk.forms import FormAction, REQUESTED_SLOT

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from database_connection import JobConnectionAPI
from database_connection import CandidateConnectionAPI
import datetime
import psycopg2
import database_connection


class ActionSearchJobs(Action):
    def name(self):
        """Unique identifier of the form"""
        return 'action_search_jobs'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("looking for jobs")
        
        job = tracker.get_slot('job_title')
        print("job title slot : "+job)
        print("\n")

        title = job.lower().split(' ')
        job_title="'%" + "%' or lower(job_title) like '%".join(title) + "%'"
        print("job title : "+job_title)
        print("\n")

        comp = tracker.get_slot('competency')
        print("competence slot: "+str(comp))
        print("\n")
       
        singleElement = True
        for element in comp:
            if(len(element) != 1):
                singleElement = False
                break
        if singleElement:
            comp = ["".join(comp)]    
        
        c= list(map(lambda x: x.lower(), comp))
        competency="('" + "') or lower(competency_title) in ('".join(c) + "')"
        print("competency : "+competency)
        print("\n")

        degree_name = tracker.get_slot('degree_name')
        print("degree_name slot : "+degree_name)
        print("\n")

        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("date : "+str(date))
        print("\n")

        # Connect to the PostgreSQL database server

        dispatcher.utter_message("We have a position where that could work out well :" )  
        connection_api = JobConnectionAPI()
        listJob = connection_api.connection(date,job_title,competency,degree_name) 
       
        print("listJob in action: "+str(listJob)) 
        print("\n")

        if (len(listJob) == 0 ):
            listJob = ["No job match found"]
            
        return [SlotSet("matches", value=listJob)]

class ActionSearchCandidates(Action):
    def name(self):
        """Unique identifier of the form"""
        return 'action_search_candidates'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("looking for candidates")

        comp = tracker.get_slot('competency')
        print("competence slot: "+str(comp))
        print("\n")
       
        singleElement = True
        for element in comp:
            if(len(element) != 1):
                singleElement = False
                break
        if singleElement:
            comp = ["".join(comp)]    
        
        c= list(map(lambda x: x.lower(), comp))
        competency=str(tuple(c))
        print("competency : "+competency)
        print("\n")

        lang=tracker.get_slot('language')
        print(lang)
        singleElement = True
        for elemnt in comp:
            if(len(elemnt) != 1):
                singleElement = False
                break
        if singleElement:
            lang = ["".join(lang)]
        
        l = list(map(lambda x: x.lower(), lang))
        
        language=str(tuple(l))
        print("language : "+language)
        print("\n")    

        degree_name = tracker.get_slot('degree_name')
        print("degree_name slot : "+degree_name)
        print("\n")

        # Connect to the PostgreSQL database server
   
        connection_api = CandidateConnectionAPI()
        listCandidate = connection_api.connection(competency,language,degree_name) 
       
        print("listJob in action: "+str(listCandidate)) 
        print("\n")

        if (len(listCandidate) == 0 ):
            listCandidate = ["No job match found"]
        else :
            dispatcher.utter_message("Favor candidates are :" )    
            
        return [SlotSet("matches", value=listCandidate)]

class ActionGetJobMatch(Action):
    def name(self):
        return 'action_get_jobs'

    def run(self, dispatcher, tracker, domain):
        job = tracker.get_slot("matches")
        dispatcher.utter_message(str(job))
        return []       

class ActionGetCandidateMatch(Action):
    def name(self):
        return 'action_get_candidates'

    def run(self, dispatcher, tracker, domain):
        candidate = tracker.get_slot("matches")
        dispatcher.utter_message(str(candidate))
        return []

class ActionSuggest(Action):
    def name(self):
        return 'action_suggest'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("here's what I found:")
        dispatcher.utter_message(tracker.get_slot("matches"))
        dispatcher.utter_message("is it ok for you? "
                                 "hint: I'm not going to "
                                 "find anything else :)")
        return []

class JobForm(FormAction):
    """Example of a custom form action"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        return "job_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["job_title", "industry", "degree_name", "name",
                "career_level", "employment_type", "competency", "location", "company"]

    
    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"job_title": [self.from_entity(entity="job_title",
                                                intent=["inform","request_job","newjoob"]),
                              self.from_text(not_intent="name")],
                "industry": self.from_entity(entity="industry",
                                                intent=["inform","request_job","newjoob"]),
                "degree_name": self.from_entity(entity="degree_name",
                                                intent=["inform","request_job","newjoob"]),
                "name": self.from_entity(entity="name",
                                        intent=["inform","request_job","newjoob"]),                                                                                
                "career_level": self.from_entity(entity="career_level",
                                                intent=["inform","request_job","newjoob"]),
                "employment_type": self.from_entity(entity="employment_type",
                                                intent=["inform","request_job","newjoob"]),  
                "competency": self.from_entity(entity="competency",
                                                intent=["inform","request_job","newjoob"]),
                "location": self.from_entity(entity="location",
                                            intent=["inform","request_job","newjoob"]), 
                "company": self.from_entity(entity="company",
                                            intent=["inform","request_job","newjoob"])}

    @staticmethod
    def degree_name_db():
        # type: () -> List[Text]
        """Database of supported degree_name"""
        return ["diploma",
                "vocational diploma",
                "higher diploma",
                "(advanced diploma) technical colleges",
                "bachelor''s degree",
                "master''s degree",
                "ph.d."]

    @staticmethod
    def career_level_db():
        # type: () -> List[Text]
        """Database of supported career_level"""
        return ["semi-skilled",
                "professional",
                "skilled",
                "un-skilled",
                "senior management",
                "supervisor"]            
               
    @staticmethod
    def employment_type_db():
        # type: () -> List[Text]
        """Database of supported employment_type"""
        return ["full-time",
                "part-time",
                "casual",
                "contractual",
                "fixed term",
                "shiftworkers",
                "daily hire and weekly hire",
                "probation",
                "outworkers"]
    
    @staticmethod
    def industry_name_db():
        # type: () -> List[Text]
        """Database of supported industry"""
        return ["agriculture, forestry, fishing and hunting",
                "mining, quarrying, and oil and gas extraction",
                "utilities",
                "construction",
                "wholesale trade",
                "information and cultural industries",
                "finance and insurance",
                "management of companies and enterprises",
                "administrative and support, waste management and remediation services",
                "educational services",
                "health care and social assistance",
                "accommodation and food services",
                "other services (except public administration)",	
                "public administration",
                "unclassified",
                "industry",
                "tourism",
                "government companies",
                "free zone",
                "logistics",
                "other sectors"]
	

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher,
                                                           tracker, domain))
            if not slot_values:
                # reject form action execution
                # if some slot was requested but nothing was extracted
                # it will allow other policies to predict another action
                raise ActionExecutionRejection(self.name(),
                                               "Failed to validate slot {0} "
                                               "with action {1}"
                                               "".format(slot_to_fill,
                                                         self.name()))

        # we'll check when validation failed in order
        # to add appropriate utterances
        for slot, value in slot_values.items():
            if slot == 'industry':
                print("industry value.lower() "+value.lower())
                if value.lower() not in self.industry_name_db():
                    dispatcher.utter_template('utter_wrong_industry', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None
            elif slot == 'degree_name':
                print("degree_name value.lower() "+value.lower())
                if value.lower() not in self.degree_name_db():
                    dispatcher.utter_template('utter_wrong_degree_name', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None 
            elif slot == 'career_level':
                print("career_levely value.lower() "+value.lower())
                if value.lower() not in self.career_level_db():
                    dispatcher.utter_template('utter_wrong_career_level', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None 
            elif slot == 'employment_type':
                if value.lower() not in self.employment_type_db():
                    dispatcher.utter_template('utter_wrong_employment_type', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None                      
        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_template('utter_submit', tracker)
        return []

###################################
class CandidateForm(FormAction):
    """Example of a custom form action"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        return "candidate_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["name", "gender", "industry", "degree_name", "candidate_competency", "language","experience", "location"]

    
    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"industry": self.from_entity(entity="industry",
                                                intent=["inform","request_candidate"]),
                "gender": self.from_entity(entity="gender",
                                                intent=["inform","request_candidate"]),
                "degree_name": self.from_entity(entity="degree_name",
                                                intent=["inform","request_candidate"]),
                "name": self.from_entity(entity="name",
                                        intent=["inform","request_candidate","name"]),                                                                                 
                "candidate_competency": self.from_entity(entity="competency",
                                                intent=["inform","request_candidate"]),
                "experience": self.from_entity(entity="experience",
                                            intent=["inform","request_candidate"]),                                
                "location": self.from_entity(entity="location",
                                            intent=["inform","request_candidate"]), 
                "language": self.from_entity(entity="language",
                                            intent=["inform","request_candidate"])}

    @staticmethod
    def degree_name_db():
        # type: () -> List[Text]
        """Database of supported degree_name"""
        return ["diploma",
                "vocational diploma",
                "higher diploma",
                "(advanced diploma) technical colleges",
                "bachelor''s degree",
                "master''s degree",
                "ph.d."]

    
    @staticmethod
    def industry_name_db():
        # type: () -> List[Text]
        """Database of supported industry"""
        return ["agriculture, forestry, fishing and hunting",
                "mining, quarrying, and oil and gas extraction",
                "utilities",
                "construction",
                "wholesale trade",
                "information and cultural industries",
                "finance and insurance",
                "management of companies and enterprises",
                "administrative and support, waste management and remediation services",
                "educational services",
                "health care and social assistance",
                "accommodation and food services",
                "other services (except public administration)",	
                "public administration",
                "unclassified",
                "industry",
                "tourism",
                "government companies",
                "free zone",
                "logistics",
                "other sectors"]
	
    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher,
                                                           tracker, domain))
            if not slot_values:
                # reject form action execution
                # if some slot was requested but nothing was extracted
                # it will allow other policies to predict another action
                raise ActionExecutionRejection(self.name(),
                                               "Failed to validate slot {0} "
                                               "with action {1}"
                                               "".format(slot_to_fill,
                                                         self.name()))

        # we'll check when validation failed in order
        # to add appropriate utterances
        for slot, value in slot_values.items():
            if slot == 'industry':
                print("industry value.lower() "+value.lower())
                if value.lower() not in self.industry_name_db():
                    dispatcher.utter_template('utter_wrong_industry', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None
            elif slot == 'degree_name':
                print("degree_name value.lower() "+value.lower())
                if value.lower() not in self.degree_name_db():
                    dispatcher.utter_template('utter_wrong_degree_name', tracker)
                    # validation failed, set slot to None
                    slot_values[slot] = None 
                           
        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_template('utter_submit', tracker)
        return []        