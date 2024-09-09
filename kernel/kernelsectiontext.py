from kernel.kernelsection import KernelSection
from kernel.kerneltext import KernelText


class KernelSectionText(KernelSection):
    def __init__(self):
        KernelSection.__init__()
        self.text_list = []

    def add_text(self, text_hex):
        if self.text_list:
            offset = self.text_list[-1].offset + self.text_list[-1].get_size()
        else:
            offset = 0
        self.text_list.append(KernelText(text_hex=text_hex, offset=offset))
    def insert_text(self, index, text_hex):
        if index == len(self.text_list):
            self.add_text(text_hex)
        elif index > len(self.text_list):
            print("Can't insert text")
            return
        else:#TODO
            pass
            #last_offset = self.text_list[index].offset
            #self.text_list.insert()
            #for i in range(index, len(self.text_list))

