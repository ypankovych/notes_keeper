from datetime import timedelta, datetime


class StateObject(dict):
    __getattr__ = dict.__getitem__


class FSM:
    def __init__(self, default):
        self.default = default
        self.states = {}
        self.extra_states = {}
        self.expired_states = {}

    def init_state(self, holder):
        """
        Sets the key to the default value
        Does the same as function set_default_state()
        :param holder: key
        :return:
        """
        self.set_default_state(holder)

    def set_state(self, holder, value):
        """
        Sets the state for the key
        :param holder: key
        :param value:
        :return:
        """
        self.states.update({holder: value})

    def remove_state(self, holder):
        """
        remove the state by holder
        :param holder: key
        :return:
        """
        if self.states.get(holder):
            del self.states[holder]

    def remove_extra_state(self, holder):
        """
        remove the extra state by holder
        :param holder: key
        :return:
        """
        del self.extra_states[holder]

    def set_default_state(self, holder):
        self.states[holder] = self.default

    def add_extra_state(self, holder, key, value):
        """
        Here you can add many values ​​for the key, they will be available like this:
        key.value
        :param holder: key
        :param key: key
        :param value:
        :return:
        """
        if not self.extra_states.get(holder):
            self.extra_states.update({holder: {key: value}})
        else:
            self.extra_states[holder].update({key: value})

    def get_state(self, holder):
        """
        return current state for holder
        :param holder: key
        :return:
        """
        return self.states.get(holder)

    def get_extra_state(self, holder, key):
        """
        return extra state for holder by name
        :param holder: key
        :param key:
        :return:
        """
        return self.extra_states.get(holder, {}).get(key)

    def all_extra_states(self, holder):
        """
        return all extra state for holder
        :param holder: key
        :return:
        """
        return StateObject(self.extra_states[holder])

