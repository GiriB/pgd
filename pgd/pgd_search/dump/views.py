from django.http import HttpResponse
from DataDump import Dump

def dataDump(request):
    """
    render the results of the search as a TSV (tab separated file)
    and return it to the user as a download
    """
    dump = Dump(request.session['search'])
    response = HttpResponse(dump, mimetype="text/tab-separated-values")
    response['Content-Disposition'] = 'attachment; filename="data.tsv"'

    return response
