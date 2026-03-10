class BaseReporter:

    def publish(self, review, finding):
        raise NotImplementedError("Reporter must implement publish()")