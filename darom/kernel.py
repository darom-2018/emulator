from darom.resource import Resource

class Kernel:
    def __init__(self, rm):
        self._processes = []
        self._ready_procs = []
        self._run_proc = None
        self._resources = []
        self._rm = rm

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

    def planner(self):
        p = self._ready_procs[0]
        self._ready_procs.remove(p)
        self._run_proc = p
        p.run()

    def create_process(self, process):
        self._run_proc.children.append(process)
        process.kernel = self
        process.parent = self.run_proc
        self._processes.append(process)
        self._ready_procs.append(process)
        self._ready_procs.sort(key=lambda p: p.priority, reverse=True)
        print()

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

    def request_res(self, res_name):
        res = list(filter(lambda r: r.name == res_name, self._resources))[0]
        res.wait_list.append(self._run_proc)
        self._run_proc = None

    def release_res(self, res_name):
        pass
