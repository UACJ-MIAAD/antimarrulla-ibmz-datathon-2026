"""Pacientes SINTÉTICOS para la demo. No corresponden a ninguna persona real."""
import random
from . import esquema

PERFILES = {
    "Sintético A · riesgo bajo": dict(HighBP=0, HighChol=0, CholCheck=1, BMI=23, Smoker=0, Stroke=0, HeartDiseaseorAttack=0,
                                      PhysActivity=1, Fruits=1, Veggies=1, HvyAlcoholConsump=0, AnyHealthcare=1, NoDocbcCost=0,
                                      GenHlth=2, MentHlth=0, PhysHlth=0, DiffWalk=0, Sex=0, Age=4, Education=6, Income=7),
    "Sintético B · riesgo intermedio": dict(HighBP=1, HighChol=0, CholCheck=1, BMI=29, Smoker=1, Stroke=0, HeartDiseaseorAttack=0,
                                            PhysActivity=1, Fruits=0, Veggies=1, HvyAlcoholConsump=0, AnyHealthcare=1, NoDocbcCost=0,
                                            GenHlth=3, MentHlth=3, PhysHlth=2, DiffWalk=0, Sex=1, Age=8, Education=4, Income=5),
    "Sintético C · riesgo alto": dict(HighBP=1, HighChol=1, CholCheck=1, BMI=36, Smoker=1, Stroke=0, HeartDiseaseorAttack=1,
                                      PhysActivity=0, Fruits=0, Veggies=0, HvyAlcoholConsump=0, AnyHealthcare=1, NoDocbcCost=1,
                                      GenHlth=4, MentHlth=5, PhysHlth=15, DiffWalk=1, Sex=1, Age=10, Education=3, Income=2),
}


def aleatorio(semilla=None):
    rnd = random.Random(semilla)
    r = {n: rnd.randint(lo, hi) for n, lo, hi in esquema.VARIABLES}
    r["BMI"] = rnd.randint(18, 45)
    return r
