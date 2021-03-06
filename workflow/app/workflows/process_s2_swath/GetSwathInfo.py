import luigi
import os
import json
from luigi import LocalTarget
from luigi.util import requires
from process_s2_swath.PrepareRawGranules import PrepareRawGranules
from process_s2_swath.GetGranuleInfo import GetGranuleInfo

@requires(PrepareRawGranules)
class GetSwathInfo(luigi.Task):
    """
    Creates a list of the products that we will be processing and some basic infor extracted from the
    product name, this will be in the form of;

    {
        "products": [
            {
                "productPath": "/app/extracted/S2B_MSIL1C_20190226T111049_N0207_R137_T30UXD_20190226T163538",
                "productName": "S2B_MSIL1C_20190226T111049_N0207_R137_T30UXD_20190226T163538",
                "date": "20190226",
                "tileId": "T30UXD",
                "satellite": "S2B"
            },
            {
                "productPath": "/app/extracted/S2B_MSIL1C_20190226T111049_N0207_R137_T31UCT_20190226T163538",
                "productName": "S2B_MSIL1C_20190226T111049_N0207_R137_T31UCT_20190226T163538",
                "date": "20190226",
                "tileId": "T31UCT",
                "satellite": "S2B"
            },
            ...
        ]
    }
    """
    paths = luigi.DictParameter()

    def run(self):
        with self.input().open('r') as prepRawFile:
            prepRawInfo = json.loads(prepRawFile.read())

        tasks = []
        for product in prepRawInfo["products"]:
            tasks.append(GetGranuleInfo(paths=self.paths, productPath=product))

        yield tasks

        products = []
        for task in tasks:
            with task.output().open('r') as taskOutput:
                submittedProduct = json.load(taskOutput)
                products.append(submittedProduct)

        output = {
            "products": products
        }

        with self.output().open("w") as o:
            json.dump(output, o, indent=4)

    def output(self):
        outFile = os.path.join(self.paths['state'], 'GetSwathInfo.json')
        return LocalTarget(outFile)