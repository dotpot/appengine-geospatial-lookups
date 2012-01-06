__author__ = 'Brian'

from Util import DataConversion

class TestRunResults:

    RunResults = {}
    # UUID of TestParameters document on CouchDB
    RunResults["TestParametersID"] = "ABC1234"

    AllSearchResultsDic = {}


    def AccumulateStats(self,queryNumber,queryParametersDic,queryRoundTripTime,queryStats):
        searchDataDic = {}
        searchDataDic["SearchParameters"] = queryParametersDic
        searchDataDic["QueryRoundTripTime"] = queryRoundTripTime
        searchDataDic["QueryStats"] = queryStats

        self.AllSearchResultsDic[queryNumber] = searchDataDic

    def PrintRunResultsJSON(self):
        self.RunResults["AllSearchResults"] = self.AllSearchResultsDic

        RunResultsJSON = DataConversion.dict_to_json(self.RunResults)
        print RunResultsJSON



  