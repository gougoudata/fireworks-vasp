__author__ = 'Shyue Ping Ong'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Shyue Ping Ong'
__email__ = 'ongsp@ucsd.edu'
__date__ = '1/31/14'

import logging
from pymatgen import Structure
from fireworks import FireTaskBase, FWAction, explicit_serialize
from custodian import Custodian
from custodian.vasp.jobs import VaspJob
from pymatgen.io.vaspio import Vasprun


def load_class(mod, name):
    mod = __import__(mod, globals(), locals(), [name], 0)
    return getattr(mod, name)


@explicit_serialize
class WriteVaspInputTask(FireTaskBase):
    """
    Writes VASP Input files.

    Required params:
        structure (dict): An input structure in pymatgen's Structure.to_dict
            format.
        vasp_input_set (str): A string name for the VASP input set. E.g.,
            "MPVaspInputSet" or "MITVaspInputSet".

    Optional params:
        input_set_params (dict): If the input set requires some additional
            parameters, specify them using input_set_params. E.g.,
            {"user_incar_settings": ...}.
    """

    required_params = ["structure", "vasp_input_set"]
    optional_params = ["input_set_params"]

    def run_task(self, fw_spec):
        s = Structure.from_dict(self["structure"])
        mod = __import__("pymatgen.io.vaspio_set", globals(), locals(),
                         [self["vasp_input_set"]], -1)
        vis = load_class("pymatgen.io.vaspio_set", self["vasp_input_set"])(
            **self.get("input_set_params", {}))
        vis.write_input(s, ".")


@explicit_serialize
class VaspCustodianTask(FireTaskBase):
    """
    Runs VASP using Custodian.

    Required Params:
        vasp_cmd: The command to run vasp. E.g., ["mpirun", "-np", "8",
            "vasp"].
        handlers ([str]): List of error handler names to use. See custodian
            .vasp.handlers for list of applicable handlers. Note that
            default args are assumed for all handlers for simplicity. A
            special option is "all", which simply uses a set of common
            handlers for relaxation jobs.

    Optional params:
        vasp_job_params (dict): Additional parameter settings as desired for
            custodian's VaspJob.
        custodian_params (dict): Additional parameter settings as desired for
            Custodian. E.g., to use a scratch directory, you can have {
            "scratch_dir": "..."} as specified in Custodian's scratch_dir
            options.
    """
    required_params = ["vasp_cmd", "handlers"]

    optional_params = ["vasp_job_params", "custodian_params"]

    def run_task(self, fw_spec):
        FORMAT = '%(asctime)s %(message)s'
        logging.basicConfig(format=FORMAT, level=logging.INFO,
                            filename="run.log")
        job = VaspJob(vasp_cmd=self["vasp_cmd"],
                      **self.get("vasp_job_params", {}))

        if self["handlers"] == "all":
            hnames = ["VaspErrorHandler", "MeshSymmetryErrorHandler",
                      "UnconvergedErrorHandler", "NonConvergingErrorHandler",
                      "PotimErrorHandler", "PBSWalltimeHandler"]
        else:
            hnames = self["handlers"]
        handlers = [load_class("custodian.vasp.handlers", n) for n in hnames]
        c = Custodian(handlers, [job], **self.get("custodian_params", {}))
        output = c.run()
        return FWAction(stored_data=output)


@explicit_serialize
class VaspAnalyzeTask(FireTaskBase):
    """
    Read in vasprun.xml and insert into Fireworks stored_data.
    """

    optional_params = ["vasprun_fname"]

    def run_task(self, fw_spec):
        f = self.get("vasprun_fname", "vasprun.xml")
        v = Vasprun(f)
        return FWAction(stored_data={"vasprun": v.to_dict})