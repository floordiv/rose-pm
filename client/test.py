from time import time
from rcore import Session
import transmission


session = Session()
session.request('download', False, login='floordiv', repo='repos_docs', version='anyversion1')
trnsmsn = transmission.Transmission(session, 'floordiv', 'repos_docs', 'anyversion1')
trnsmsn.start()
