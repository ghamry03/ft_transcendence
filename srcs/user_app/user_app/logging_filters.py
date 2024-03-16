# in your logging_filters.py or wherever it's convenient
import logging

class RequestFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        if message.find('GET') != -1:
            print(f'FOUND')
            return False
        print(f'NOT FOUND')
        return True