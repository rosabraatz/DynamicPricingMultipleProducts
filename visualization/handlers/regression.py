import json

import tornado.web

from core.regression import LogisticRegressor
from core.sales import SalesGeneratorFactory


class RegressionHandler(tornado.web.RequestHandler):
    # Constants
    MIN_PRICE = 1
    MAX_PRICE = 20
    PRICE_STEP = 0.5
    COMPETITORS_COUNT = 2
    OBSERVATIONS_COUNT = 1000

    def get(self):
        # Get sale probability coefficients
        coeff_A_intercept = float(self.get_argument('coeffAIntercept'))
        coeff_A_price_A = float(self.get_argument('coeffAPriceA'))
        coeff_A_price_B = float(self.get_argument('coeffAPriceB'))
        coeff_A_min_comp_A = float(self.get_argument('coeffAMinCompA'))
        coeff_A_min_comp_B = float(self.get_argument('coeffAMinCompB'))
        coeff_A_rank_A = float(self.get_argument('coeffARankA'))
        coeff_A_rank_B = float(self.get_argument('coeffARankB'))

        coeff_B_intercept = float(self.get_argument('coeffBIntercept'))
        coeff_B_price_A = float(self.get_argument('coeffBPriceA'))
        coeff_B_price_B = float(self.get_argument('coeffBPriceB'))
        coeff_B_min_comp_A = float(self.get_argument('coeffBMinCompA'))
        coeff_B_min_comp_B = float(self.get_argument('coeffBMinCompB'))
        coeff_B_rank_A = float(self.get_argument('coeffBRankA'))
        coeff_B_rank_B = float(self.get_argument('coeffBRankB'))

        # Pack coefficients
        coefficients = [
            [coeff_A_intercept, coeff_A_price_A, coeff_A_price_B,
             coeff_A_min_comp_A, coeff_A_min_comp_B, coeff_A_rank_A, coeff_A_rank_B],
            [coeff_B_intercept, coeff_B_price_A, coeff_B_price_B,
             coeff_B_min_comp_A, coeff_B_min_comp_B, coeff_B_rank_A, coeff_B_rank_B]
        ]

        # Create sale generator
        sales_generator_factory = SalesGeneratorFactory(self.MIN_PRICE, self.MAX_PRICE,
                                                        self.PRICE_STEP, self.COMPETITORS_COUNT)
        sales_generator = sales_generator_factory.create_extended()

        # Run regression
        regressor = LogisticRegressor(sales_generator, self.OBSERVATIONS_COUNT)
        result = regressor.train_iteratively(coefficients)
        coeffs, prices, competitor_prices, sale_probs, min_observations, max_observations = result

        # Write output
        self.write(json.dumps({
            'meta': {
                'minObservations': min_observations,
                'maxObservations': max_observations,
                'coeffsCount': min(len(x) for x in coeffs)
            },
            'coeffs': coeffs,
            'prices': prices.tolist(),
            'competitorPrices': competitor_prices.tolist(),
            'saleProbs': sale_probs.tolist()
        }))


