"SYNTHETIC demo patients. These profiles do not represent real people."
import random
from . import schema

PROFILES = {
    "Synthetic A · low risk": dict(HighBP=0, HighChol=0, CholCheck=1, BMI=23, Smoker=0, Stroke=0, HeartDiseaseorAttack=0,
                                      PhysActivity=1, Fruits=1, Veggies=1, HvyAlcoholConsump=0, AnyHealthcare=1, NoDocbcCost=0,
                                      GenHlth=2, MentHlth=0, PhysHlth=0, DiffWalk=0, Sex=0, Age=4),
    "Synthetic B · intermediate risk": dict(HighBP=1, HighChol=0, CholCheck=1, BMI=29, Smoker=1, Stroke=0, HeartDiseaseorAttack=0,
                                            PhysActivity=1, Fruits=0, Veggies=1, HvyAlcoholConsump=0, AnyHealthcare=1, NoDocbcCost=0,
                                            GenHlth=3, MentHlth=3, PhysHlth=2, DiffWalk=0, Sex=1, Age=8),
    "Synthetic C · high risk": dict(HighBP=1, HighChol=1, CholCheck=1, BMI=36, Smoker=1, Stroke=0, HeartDiseaseorAttack=1,
                                      PhysActivity=0, Fruits=0, Veggies=0, HvyAlcoholConsump=0, AnyHealthcare=1, NoDocbcCost=1,
                                      GenHlth=4, MentHlth=5, PhysHlth=15, DiffWalk=1, Sex=1, Age=10),
}


def random_patient(seed=None):
    rnd = random.Random(seed)
    r = {n: rnd.randint(low, high) for n, low, high in schema.VARIABLES}
    r["BMI"] = rnd.randint(18, 45)
    return r
