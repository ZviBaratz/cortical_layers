from .data_loader import DataLoader
from .subject import Subject


data_loader = DataLoader()
subjects = data_loader.subjects



class DataAccessObject:
    def __init__(self, subjects: list = subjects):
        """
        This class handles data access

        :param subjects: subjects data
        :type subjects: list of subject instances
        """
        self.subjects = subjects

    def get_subject_by_id(self, subject_id: str) -> Subject:
        return data_loader.get_subject_by_id(subject_id)
