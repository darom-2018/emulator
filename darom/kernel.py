import pdb

from darom.resource import Resource, ResourceRequest
from darom.process import Status

class Kernel:
    def __init__(self, rm):
        self._processes = []
        self._ready_procs = []
        self._run_proc = None
        self._resources = []
        self._rm = rm
        self._rm._kernel = self

        self._call_planner = True

    def __str__(self):
        str = '-----------------------Kernel--------------------\n'
        str += "Processes:\n"
        for p in self._processes:
            str += "\t{}\n".format(p)
        str += "Resources:\n"
        for r in self._resources:
            str += "\t{}\n".format(r)
        str += "Ready Processes:\n"
        for p in self.ready_procs:
            str += "\t{}\n".format(p)
        str += "Run Process:\n"
        str += "\t{}\n".format(self._run_proc)
        str += '------------------------------------------------\n'
        return str

    @property
    def processes(self):
        return self._processes

    @property
    def ready_procs(self):
        return self._ready_procs

    @property
    def run_proc(self):
        return self._run_proc

    @run_proc.setter
    def run_proc(self, run_proc):
        self._run_proc = run_proc

    def _find_res_by_name(self, res_name):
        for res in self._resources:
            if res.name == res_name:
                return res
        raise Exception("Resource '{}' not found!".format(res_name))

    def remove_blocked_processes(self):
        for p in self._ready_procs:
            st = p.status
            if st == Status.BLOCK or st == Status.BLOCKS or st == Status.READYS:
                self._ready_procs.remove(p)

    def planner(self):
        self._planner_works = True
        while self._call_planner:
            self._call_planner = False
            self.remove_blocked_processes()
            if self._ready_procs:
                p = self._ready_procs[0]
                self._run_proc = p
                p.run()
        self._planner_works = False

    def plan(self):
        self._call_planner = True
        if not self._planner_works:
            self.planner()

    def distributor(self):
        for res in self._resources:
            for req in res._wait_list:
                if req.amount <= len(res.elements):
                    req.proc.owned_res.extend(res.get_elements(req.amount))
                    req.proc.unblock()
                    self._ready_procs.append(req.proc)
        self.plan()


    def create_process(self, process):
        self._run_proc.children.append(process)
        process.kernel = self
        process.parent = self.run_proc
        self._processes.append(process)
        self._ready_procs.append(process)
        self._ready_procs.sort(key=lambda p: p.priority, reverse=True)

    def destroy_process(self, process):
        pass

    def stop_process(self, process):
        pass

    def activate_process(self, process):
        pass

    def create_res(self, res_name):
        res = Resource(parent=self._run_proc, name=res_name)

        self._run_proc.created_res.append(res)
        self._resources.append(res)

    def destroy_res(self, res_name):
        pass

    def request_res(self, res_name, amount):
        res = self._find_res_by_name(res_name)
        res.wait_list.append(ResourceRequest(self._run_proc, amount))
        self._run_proc.status = Status.BLOCK
        self._run_proc = None

        self.distributor()

    def release_res(self, res_name, elems):
        res = self._find_res_by_name(res_name)
        res.elements.extend(elems)

        self.distributor()
