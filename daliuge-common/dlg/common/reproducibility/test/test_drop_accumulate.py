import unittest

from dlg.common.reproducibility.constants import ReproducibilityFlags
from dlg.common.reproducibility.reproducibility import accumulate_lgt_drop_data


class TestLGTDropAccumulate(unittest.TestCase):

    def test_accumulate_lgt_application(self):
        self.lgt_a = {
            "category": "BashShellApp",
            "categoryType": "Application",
            "fields": [
                {
                    "name": "Arg01",
                    "text": "Arg01",
                    "value": "echo -en 'Hello world' > %o0"
                }
            ],
            "inputPorts": [],
            "outputPorts": [
                {
                    "Id": "3o1",
                    "IdText": "event"
                }
            ],
            "streaming": True,
        }
        self.lgt_a_out = {
            ReproducibilityFlags.RERUN: {'category_type': "Application",
                                         'category': "BashShellApp",
                                         'numInputPorts': 0,
                                         'numOutputPorts': 1,
                                         'streaming': True},
            ReproducibilityFlags.REPEAT: {'category_type': "Application",
                                          'category': "BashShellApp",
                                          'numInputPorts': 0,
                                          'numOutputPorts': 1,
                                          'streaming': True},
            ReproducibilityFlags.REPRODUCE: {'category_type': "Application",
                                             'category': "BashShellApp"},
            ReproducibilityFlags.REPLICATE_SCI: {'category_type': "Application",
                                                 'category': "BashShellApp",
                                                 'numInputPorts': 0,
                                                 'numOutputPorts': 1,
                                                 'streaming': True},
            ReproducibilityFlags.REPLICATE_COMP: {'category_type': "Application",
                                                  'category': "BashShellApp",
                                                  'numInputPorts': 0,
                                                  'numOutputPorts': 1,
                                                  'streaming': True}
        }
        for flag, expected in self.lgt_a_out.items():
            actual = accumulate_lgt_drop_data(self.lgt_a, flag)
            self.assertEqual(actual, expected)

    def test_accumulate_lgt_data(self):
        self.lgt_d = {
            "category": "File",
            "categoryType": "Data",
            "fields": [
                {
                    "name": "check_filepath_exists",
                    "text": "Check file path exists",
                    "value": "1"
                },
                {
                    "name": "filepath",
                    "text": "File path",
                    "value": "result1.out"
                },
                {
                    "name": "dirname",
                    "text": "Directory name",
                    "value": "/home/data"
                }
            ],
            "inputPorts": [
                {
                    "Id": "2i1",
                    "IdText": "event"
                }
            ],
            "isData": True,
            "isGroup": False,
            "outputPorts": [],
            "streaming": False,
        }
        self.lgt_d_out = {
            ReproducibilityFlags.RERUN: {'category_type': "Data",
                                         'category': "File",
                                         'numInputPorts': 1,
                                         'numOutputPorts': 0,
                                         'streaming': False},
            ReproducibilityFlags.REPEAT: {'category_type': "Data",
                                          'category': "File",
                                          'numInputPorts': 1,
                                          'numOutputPorts': 0,
                                          'streaming': False},
            ReproducibilityFlags.REPRODUCE: {'category_type': "Data",
                                             'category': "File"},
            ReproducibilityFlags.REPLICATE_SCI: {'category_type': "Data",
                                                 'category': "File",
                                                 'numInputPorts': 1,
                                                 'numOutputPorts': 0,
                                                 'streaming': False},
            ReproducibilityFlags.REPLICATE_COMP: {'category_type': "Data",
                                                  'category': "File",
                                                  'numInputPorts': 1,
                                                  'numOutputPorts': 0,
                                                  'streaming': False}
        }
        for flag, expected in self.lgt_d_out.items():
            actual = accumulate_lgt_drop_data(self.lgt_d, flag)
            self.assertEqual(actual, expected)

    def test_accumulate_lgt_group(self):
        self.lgt_g = {
            "category": "Scatter",
            "categoryType": "Group",
            "exitAppName": "",
            "fields": [
                {
                    "name": "num_of_copies",
                    "text": "Number of copies",
                    "value": "4"
                },
                {
                    "name": "scatter_axis",
                    "text": "Scatter axis",
                    "value": "time"
                }
            ],
            "inputLocalPorts": [
                {
                    "Id": "88f46618-57ac-4e9c-99a7-f9cf2d682852",
                    "IdText": "event"
                }
            ],
            "inputPorts": [
                {
                    "Id": "b8cc69ef-de0c-4c6a-bba2-df12aff17a8b",
                    "IdText": "event"
                }
            ],
            "isData": False,
            "isGroup": True,
            "outputLocalPorts": [
                {
                    "Id": "c29554bd-8003-410a-9cce-c0d4376bb1ef",
                    "IdText": "event"
                }
            ],
            "outputPorts": [
                {
                    "Id": "a8e147cb-065c-49ee-8c52-25c53cf36a07",
                    "IdText": "event"
                }
            ],
            "streaming": False
        }
        self.lgt_g_out = {
            ReproducibilityFlags.RERUN: {'category_type': "Group",
                                         'category': "Scatter",
                                         'numInputPorts': 1,
                                         'numOutputPorts': 1,
                                         'streaming': False},
            ReproducibilityFlags.REPEAT: {'category_type': "Group",
                                          'category': "Scatter",
                                          'numInputPorts': 1,
                                          'numOutputPorts': 1,
                                          'streaming': False},
            ReproducibilityFlags.REPRODUCE: {'category_type': "Group",
                                             'category': "Scatter"},
            ReproducibilityFlags.REPLICATE_SCI: {'category_type': "Group",
                                                 'category': "Scatter",
                                                 'numInputPorts': 1,
                                                 'numOutputPorts': 1,
                                                 'streaming': False},
            ReproducibilityFlags.REPLICATE_COMP: {'category_type': "Group",
                                                  'category': "Scatter",
                                                  'numInputPorts': 1,
                                                  'numOutputPorts': 1,
                                                  'streaming': False}
        }
        for flag, expected in self.lgt_g_out.items():
            actual = accumulate_lgt_drop_data(self.lgt_g, flag)
            self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
