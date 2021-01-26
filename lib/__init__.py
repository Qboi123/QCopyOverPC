class FileSize(object):
    @staticmethod
    def get_string(size: int):
        if size < 1024:
            return f"{round(size, 1)} B"
        elif size < 1024 ** 2:
            return f"{round(size / 1024, 1)} KB"
        elif size < 1024 ** 3:
            return f"{round(size / (1024 ** 2), 1)} MB"
        elif size < 1024 ** 4:
            return f"{round(size / (1024 ** 3), 1)} GB"
        elif size < 1024 ** 5:
            return f"{round(size / (1024 ** 4), 1)} TB"
        elif size < 1024 ** 6:
            return f"{round(size / (1024 ** 5), 1)} PB"
        elif size < 1024 ** 7:
            return f"{round(size / (1024 ** 6), 1)} EB"
        elif size < 1024 ** 8:
            return f"{round(size / (1024 ** 7), 1)} ZB"
        elif size < 1024 ** 9:
            return f"{round(size / (1024 ** 8), 1)} YB"
        else:
            return f"OverflowError"
