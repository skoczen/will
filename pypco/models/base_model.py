"""Provides the base model object from which all other models inherit.
"""

import copy
from .. import models

class BaseModel():
    """Base model class from which all models inherit."""

    def __init__(self, endpoint, data=None, user_created=False, from_get=False):
        """Initialize the model class.

        Args:
            endpoint (BaseEndpoint): The endpoint associated with this object.
            data (dict): The dict from which to build object properties.
            user_created (boolean): Was this model created by a user?
            get (boolean): Was this model created by a direct get request?
        """

        self._endpoint = endpoint
        self._data = data
        self._update_attribs = set()
        self._update_relationships = set()
        self._user_created = user_created
        self._from_get = from_get
        self.rel = RelationWrapper(self)

    def __getattr__(self, name):
        """Magic method to dynamically get object properties.
        
        Model attributes are dynamically available based on the data returned by the PCO API.
        To determine what attributes are/aren't available, check the PCO API docs.

        Args:
            name (str): The attribute name

        Returns:
            The attribute value as a string.

        Raises:
            AttributeError: Thrown if the property does not exist on the object.
        """

        # Search this object's attribs
        search_dicts = [
            self._data,
            self._data['attributes']
        ]

        for search_dict in search_dicts:
            if name in search_dict.keys():
                return search_dict[name]

        raise AttributeError("'{}' is not an available attribute on this object.".format(name))

    def __setattr__(self, name, value):
        """Magic method to facilitate handling object properties.

        If the attribute name begins with an underscore (a "private" variable),
        we go ahead and set it on the object. If it does not begin with an underscore,
        we set it in the attributes dict of the model's data dictionary. We don't
        do any validation on attributes that are set; we'll let the PCO API do
        this for us.

        Args:
            name (str): The name of the attribute to set.
            value (object):  The value to set for the specified attribute.
        """

        if name[0] == '_' or name == 'rel':
            object.__setattr__(self, name, value)
        else:
            self._data['attributes'][name] = value
            self._update_attribs.add(name)

    def delete(self):
        """Delete this object.

        WARNING: This is most likely permanent. Make sure you're REALLY
        sure you want to delete this object on PCO before calling this function.

        Raises:
            PCOModelStateError: Raised if the state of the current object is invalid
            for this function call (i.e., you cannot delete an object that hasn't been
            pulled from PCO at some point during its lifecycle.)
        """

        if self._user_created == True or not self._data or not 'id' in self._data:
            raise PCOModelStateError("Couldn't delete this object; it appears it was never synced with PCO.")

        self._endpoint.delete(self.links['self'])

    def update(self):
        """Update any changes you've made to the current object in PCO.

        Raises:
            PCOModelStateError: Raised if the state of the current object is invalid
            for this function call. This would be the case if the current object has
            never been connected PCO (i.e., one you create new but never actually created
            on the PCO API via the create function).
        """

        if self._user_created == True or not self._data or not 'id' in self._data:
            raise PCOModelStateError("Couldn't delete this object; it appears it was never synced with PCO.")

        self._data = self._endpoint.update(self.links['self'], self._serialize_updates())['data']

        self._update_attribs = set()
        self._update_relationships = set()

    def create(self):
        """Create the current object as a new object in PCO.

        Raises:
            PCOModelStateError: Raised if the state of the current object is invalid
            for this function call. This would be the case if the current object was
            retrieved from PCO and/or has already been created in PCO.
        """

        if self._from_get or not self._user_created or 'id' in self._data:
            raise PCOModelStateError()

        self._data = self._endpoint.create(
            self._endpoint.get_full_endpoint_url(),
            {'data': self._data}
        )['data']

        self._from_get = True
        self._user_created = False
        self._update_attribs = set()
        self._update_relationships = set()
    
    def refresh(self, hard = False):
        """Refresh the object with current data from the PCO API.

        By default, this does a "soft" refresh; any properties changed on the object
        by the user will not be overwritten. If overwriting changed properties is desired,
        specify the "hard" parameter with a value of "True".
        
        Args:
            hard (bool): Specify whether or not we should do a hard refresh.
        """

        if not 'id' in self._data or not 'type' in self._data or self._user_created:
            raise PCOInvalidModelError(
                "Model not synced with PCO. Refresh can only be called on models that have been synced with PCO."
            )

        # Save the updates, if not a hard refresh
        if not hard:
            updates = self._serialize_updates()['data']

        # Reload from PCO
        refr_obj = self._endpoint.get_by_url(self.links['self'])
        self._data = refr_obj.data
        self._from_get = True

        # Restore stuff, if not a hard refresh
        if not hard:
            # Restore attributes
            if 'attributes' in updates:
                if not 'attributes' in self._data:
                    self._data['attributes'] = {}

                for attrib,value in updates['attributes'].items():
                    self._data['attributes'][attrib] = value
            
            # Restore relationships
            if 'relationships' in updates:
                if not 'relationships' in self._data:
                    self._data['relationships'] = {}

                for attrib,value in updates['relationships'].items():
                    self._data['relationships'][attrib] = value

    def _serialize_updates(self):
        """Get updated attributes to be pushed to PCO.

        Returns:
            A dictionary representing only the changed attributes to be pushed to PCO.
        """

        data = { 
            'data': {
                'type': self.type,
                'id': self.id
            }
        }

        if len(self._update_attribs) > 0:
            data['data']['attributes'] = {key:self._data['attributes'][key] for key in self._update_attribs}

        if len(self._update_relationships) > 0:
            data['data']['relationships'] = {key:self._data['relationships'][key] for key in self._update_relationships}

        return data

    @property
    def data(self):
        """Get a copy of this object's raw data structure.
        
        Returns:
            A copy of the dict object that stores this object's raw data from
            the PCO API.
        """
        
        return copy.deepcopy(self._data)

    # TODO: Build a "from_dict" function with the ability to load attributes from a dict

    def __str__(self):
        """Return the string representation of this object."""

        return str(self._data)

    def __repr__(self):
        """Return the string representation of this object."""

        return self.__str__()

class RelationWrapper():
    """A wrapper class for relationship management. 

    This technique allows relationship names to be specified as model properties
    rather than as function arguments.

    Examples manipulating objects with relationships:
        >>> import pypco
        >>> pco = pypco.PCO("<app_id>", "<app_secret>")
        >>> # Add a relationship with an existing linked object
        >>> school = pco.people.school_options.get("12345")
        >>> person = pco.people.people.get("12345")
        >>> person.rel.school.set(school)
        >>> person.update()
        >>> # Add a relationship with a new linked object
        >>> address = pco.new(pypco.models.people.Address)
        >>> address.city = "Camelot"
        >>> address.location = "Home"
        >>> address.state = "Pa"
        >>> address.street = "123 Round Table Rd"
        >>> address.zip = "12345"
        >>> person.rel.addresses.add(address)
        >>> person.update()
        >>> # Create a new household
        >>> person1 = pco.people.people.get("12345")
        >>> person2 = pco.people.people.get("23456")
        >>> household = pco.new(pypco.models.people.household)
        >>> household.people.add(person1)
        >>> household.people.add(person2)
        >>> household.rel.primary_contact.set(person1)
        >>> household.update()
    """

    def __init__(self, model):
        """Initialize the RelationWrapper object.
        
        Args:
            parent_model (BaseModel): The parent model object for this relationship manager.
        """

        self._model = model

    def __getattr__(self, name):
        """Resolve relationship names and return an initialized RelationManager."""

        return RelationManager(name, self._model)

class RelationManager():
    """Provides facilities for managing relationships between objects."""

    def __init__(self, rel_name, model):
        """Initialize the RelationshipManager object."""

        self._rel_name = rel_name
        self._model = model

        # If we don't have a relationships key, create it
        if not 'relationships' in self._model._data:
            self._model._data['relationships'] = {}

        self._relationships = self._model._data['relationships']

    def get(self):
        """Get the association in a to-one relationship.
        
        Returns:
            BaseModel: An object inheriting from BaseModel that corresponds
            to the PCO API object specified in the relationship. Returns None
            if the requested relation has a None or null value.

        Raises:
            PCORelationDoesNotExistError: The requested relation does not exist on this model.
        """

        # If this wasn't a direct get request, refresh to make sure
        # we have all available links, unless the model is newly created
        if not self._model._from_get and not self._model._user_created:
            self._model.refresh()

        # If we have a matching link, fetch via the links attribute
        # Unless we've made updates to the object's relationships
        # In that case, fetch from relationships
        if ('links' in self._model._data and 
            self._rel_name in self._model._data['links'] and
                not self._rel_name in self._model._update_relationships):
            
            # Return None/null value if that's what we have, and there's nothing in 
            if self._model._data['links'][self._rel_name] == None:
                return None
            
            # We now know we have a value in links and it's not null; fetch and return
            return self._model._endpoint.get_by_url(self._model._data['links'][self._rel_name])

        # We don't have a matching link; raise an error if we don't have
        # a matching relationship
        if not self._rel_name in self._relationships:
            raise PCORelationDoesNotExistError("The relation or link \"{}\" does not exist on this object.".format(self._rel_name))

        # We know we have a matching relationship; let's check for a None value
        if self._relationships[self._rel_name]['data'] == None:
            return None

        # The relationship exists and is not None; fetch and return
        return self._get_relation_endpoint().get(
            self._relationships[self._rel_name]['data']['id']
        )

    def list(self, where={}, filter=[], per_page=None, order=None, **kwargs):
        """Get the associated objects in a to-many relationship.

        Args:
            where (dict): Query parameters specified as a dictionary. See PCO API docs for valid params.
            filter (list): Filter parameters for the query. See PCO API docs for valid filter params.
            per_page (int): How many items to retrieve per page. Defaults to PCO default of 25.
            order (str): The field by which to order results. Defaults to PCO API default (sorted by ID).
            kwargs (str): Any additional kwargs will added directly to the request as query params.

        Returns:
            Generator: A generator that loops over the related objects (which will
            inherit from the BaseModel class). Generator will yield no objects if
            no results are found.

        Raises:
            PCORelationDoesNotExistError: The requested relation does not exist on this model.
        """

        # If this wasn't a direct get request, refresh to make sure
        # we have all available links, unless the model is newly created
        if not self._model._from_get and not self._model._user_created:
            self._model.refresh()

        # If we have a matching link, fetch via the links attribute
        # Unless we've made updates to the object's relationships
        # In that case, fetch from relationships
        if ('links' in self._model._data and 
            self._rel_name in self._model._data['links'] and
                not self._rel_name in self._model._update_relationships):

            return self._model._endpoint.list_by_url(
                self._model._data['links'][self._rel_name],
                where=where,
                filter=filter,
                per_page=None,
                order=None,
                **kwargs
            )

        # We don't have a matching link, or relatinships were updated; raise an error if we don't have
        # a matching relationship
        if not self._rel_name in self._relationships:
            raise PCORelationDoesNotExistError("The relation or link \"{}\" does not exist on this object.".format(self._rel_name))
        
        # We know the relationship is present
        # Return an iterator 
        return self._get_relationship_generator(
            self._relationships[self._rel_name]['data']
        )

    def set(self, model):
        """Set the association on this object in a to-one relationship"""

        # Ensure we got a model object
        if not isinstance(model, models.base_model.BaseModel):
            raise PCOInvalidModelError("A valid model object is required.")

        # Ensure we have an id, type, and a model that is not newly user created
        if not 'id' in model.data or not 'type' in model.data or model._user_created:
            raise PCOInvalidModelError(
                "Model not synced with PCO. Create or retrieve your model from PCO, then try again."
            )

        # Create the key for the relationship if it doesn't exist
        if not self._rel_name in self._relationships:
            self._relationships[self._rel_name] = None

        relationship = { 'data': {} }

        relationship['data']['type'] = model.type
        relationship['data']['id'] = model.id

        self._model._update_relationships.add(self._rel_name)

        self._relationships[self._rel_name] = relationship

    def add(self, model):
        """Add an association to this object in a to-many relationship.

        Raises:
            PCOInvalidModelError: The model object passed to this function was not
            in the correct state.
        """

        # Ensure we got a model object
        if not isinstance(model, models.base_model.BaseModel):
            raise PCOInvalidModelError("A valid model object is required.")

        # Ensure our model object has a type and id
        if not 'type' in model._data or not 'id' in model._data:
            raise PCOInvalidModelError("The model is missing the \"type\" or \"id\" attribute and cannot be created.")

        # Ensure our model object is not newly created
        if model._user_created:
            raise PCOInvalidModelError("You must pass a newly created object!")

        # Try getting the existing relationships; if
        # we get a PCOInvalidModelError, there aren't any
        # on this object yet; create an empty key and set an
        # empty list of existing relationships
        try:
            relationships = [existing for existing in self.list()]
        except PCORelationDoesNotExistError:
            self._relationships[self._rel_name] = {}
            relationships = []

        relationships.append(model)

        self._relationships[self._rel_name]['data'] = []
        for model in relationships:
            self._relationships[self._rel_name]['data'].append({ 'type': model.type, 'id': model.id })

        self._model._update_relationships.add(self._rel_name)

    def unset(self):
        """Remove the association on this object in a to-one relationship."""

        # Create the key for the relationship if it doesn't exist
        if not self._rel_name in self._relationships:
            self._relationships[self._rel_name] = None

        self._model._update_relationships.add(self._rel_name)

        self._relationships[self._rel_name] = { 'data': None } 

    def remove(self, model):
        """Remove the association on this object in a to-many relationship."""

        # Ensure we got a model object
        if not isinstance(model, models.base_model.BaseModel):
            raise PCOInvalidModelError("A valid model object is required.")

        # Ensure our model object has a type and id
        if not 'type' in model._data or not 'id' in model._data:
            raise PCOInvalidModelError("The model is missing the \"type\" or \"id\" attribute and cannot be created.")

        # Ensure our model object is not newly created
        if model._user_created:
            raise PCOInvalidModelError("You must pass a newly created object!")

        relationships = [{ 'type': existing.type, 'id': existing.id } for existing in self.list()]

        index = -1
        for ndx,relationship in enumerate(relationships):
            if relationship['id'] == model.id:
                index = ndx
                break
        
        # If we didn't find the object to remove, raise an error
        if index == -1:
            raise PCOInvalidModelError("The model you specified to remove does not exist as a relationship to this object!")

        # We know it's there; do the removal
        del relationships[index]

        # Initialize the attrib for this relationship on the parent model
        self._relationships[self._rel_name] = {}
        self._relationships[self._rel_name]['data'] = []

        # Set the value of the data attrib with the new values
        self._relationships[self._rel_name]['data'] = relationships

        # Add the relationship name to our list of modified relationships
        self._model._update_relationships.add(self._rel_name)

    def create(self, model):
        """Create objects that must be created from the related object's endpoint.
        
        Note: Unlike the other functions for managing related objects, calling the
        create function immediately persists the new object to PCO. It is not necessary
        to call the update() function on the parent object afterwards to save.

        Raises:
            PCOInvalidModelError: The model object passed to this function was not
            in the correct state.
        """
        
        # Ensure we got a model object
        if not isinstance(model, models.base_model.BaseModel):
            raise PCOInvalidModelError("A valid model object is required.")

        # Ensure our model object has a type
        if not 'type' in model._data:
            raise PCOInvalidModelError("The model is missing the \"Type\" attribute and cannot be created.")

        # Ensure our model object is newly created
        if not model._user_created:
            raise PCOInvalidModelError("You must pass a newly created object!")

        # We now have reason to believe our model is good;
        # Let's create our model in the PCO API
        model._data = self._model._endpoint.create(
            "{}/{}".format(
                self._model._data['links']['self'],
                self._rel_name
            ),
            {"data": model._data}
        )['data']

        # Set/reset state tracking variables
        model._from_get = True
        model._user_created = False
        model._update_attribs = set()
        model._update_relationships = set()
 
    def _get_relationship_generator(self, records):
        """Returns a generator that iterates objects in the relationship."""

        for record in records:
            yield self._get_relation_endpoint().get(
                record['id']
            )

    def _get_relation_endpoint(self):
        """Gets the endpoint associated with a relation record.
        
        This function is called to assist in retrieving existing relation objects.

        Returns:
            BaseEndpoint: A class inheriting from BaseEndpoint corresponding to the correct
            endpoint to which requests for the related object should be made.
        """

        # Get the base endpoint
        base_endpoint = getattr(
            self._model._endpoint._api_instance,
            self._model._endpoint.get_parent_endpoint_name()
        )

        # Get the module containing the desired model's class
        model_module = getattr(
            models,
            self._model._endpoint.get_parent_endpoint_name()
        )

        data_type = None

        # Get the desired model's class
        if type(self._model._data['relationships'][self._rel_name]['data']) is list:
            data_type = self._model._data['relationships'][self._rel_name]['data'][0]['type']
        else:
            data_type = self._model._data['relationships'][self._rel_name]['data']['type']

        model_class = getattr(
            model_module,
            data_type
        )

        # Get the necessary endpoint, using ENPOINT_NAME from the model class to
        # resolve the correct endpoint
        return getattr(base_endpoint, model_class.ENDPOINT_NAME)

class PCOModelStateError(Exception):
    """An exception representing a function call against a model that is
    in an invalid state."""

    pass

class PCOInvalidModelError(Exception):
    """Exception raised when an invalid model as provided as a function argument."""

    pass

class PCORelationDoesNotExistError(Exception):
    """An exception thrown when the requested relation does not exist on the current object."""

    pass