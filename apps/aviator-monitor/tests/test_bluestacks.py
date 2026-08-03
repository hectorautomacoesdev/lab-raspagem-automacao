"""Testes offline do controle do BlueStacks — só as funções puras de conf (sem tocar no real)."""
from aviator_monitor.device.bluestacks import (
    parse_conf,
    set_conf_line,
    instance_names_from_conf,
)

SAMPLE = '\n'.join([
    "# comentario",
    'bst.enable_adb_access="1"',
    'bst.installed_images="Nougat32,Rvc64"',
    'bst.instance.Rvc64.adb_port="5555"',
    'bst.instance.Rvc64.status.adb_port="5565"',
    'bst.instance.Rvc64.ram="4096"',
    "",
]) + "\n"


def test_parse_conf_strips_quotes_and_comments():
    conf = parse_conf(SAMPLE)
    assert conf["bst.enable_adb_access"] == "1"
    assert conf["bst.instance.Rvc64.ram"] == "4096"
    assert "# comentario" not in conf


def test_instance_names():
    assert instance_names_from_conf(parse_conf(SAMPLE)) == ["Nougat32", "Rvc64"]


def test_set_conf_line_replaces_existing():
    out = set_conf_line(SAMPLE, "bst.enable_adb_access", "0")
    assert 'bst.enable_adb_access="0"' in out
    assert 'bst.enable_adb_access="1"' not in out
    # não duplica a linha
    assert out.count("bst.enable_adb_access=") == 1


def test_set_conf_line_appends_new_key():
    out = set_conf_line(SAMPLE, "bst.new_key", "hello")
    assert 'bst.new_key="hello"' in out
    # preserva as chaves antigas
    assert parse_conf(out)["bst.installed_images"] == "Nougat32,Rvc64"


def test_set_conf_line_preserves_other_values():
    out = set_conf_line(SAMPLE, "bst.instance.Rvc64.adb_port", "6000")
    conf = parse_conf(out)
    assert conf["bst.instance.Rvc64.adb_port"] == "6000"
    assert conf["bst.instance.Rvc64.status.adb_port"] == "5565"  # intacta
    assert conf["bst.instance.Rvc64.ram"] == "4096"
