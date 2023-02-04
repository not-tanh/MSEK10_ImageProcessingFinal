class Pipeline:
    def __init__(self, module_list):
        self.module_list = module_list

    def __call__(self, image, **kwargs):
        out = image
        for module in self.module_list:
            out = module(out)
        return out
