import pytest
from engine.floorplan import validate_floorplan, FloorplanError, ANDAR_STATUS

def test_floorplan_valido():
    fp = {"objetivo": "simulador de caixa", "objetivo_confirmado": True,
          "diagnostico": "no-caminho",
          "andares": [{"nivel": "ideacao", "status": "cheio"},
                      {"nivel": "concepcao", "status": "provisional"},
                      {"nivel": "codigo", "status": "vazio"}]}
    assert validate_floorplan(fp) == fp

def test_diagnostico_fechado():
    fp = {"objetivo": "x", "objetivo_confirmado": False, "diagnostico": "voando",
          "andares": []}
    with pytest.raises(FloorplanError, match="diagnostico"):
        validate_floorplan(fp)

def test_andar_status_fechado():
    fp = {"objetivo": "x", "objetivo_confirmado": True, "diagnostico": "girando",
          "andares": [{"nivel": "ideacao", "status": "meio-cheio"}]}
    with pytest.raises(FloorplanError, match="status"):
        validate_floorplan(fp)
    assert ANDAR_STATUS == {"cheio", "provisional", "vazio"}
