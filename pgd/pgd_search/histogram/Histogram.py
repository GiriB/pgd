import math

import cairo
from django.db.models import Max, Min, Count

from pgd_constants import *
from pgd_core.models import *
from pgd_search.models import *
from svg import *
from pgd_search.statistics.aggregates import BinSort


ANGLES = ('ome', 'phi', 'psi', 'chi1','chi2','chi3','chi4', 'zeta')

class HistogramPlot():
    
    def __init__(self, query, X, Xm, Y, Ym, histoX, histoY, histoZ, histoXr, histoYr, histoZr):
        
        self.minXPix = 35
        self.minYPix = 9
        self.maxXPix = 245
        self.maxYPix = 170
        self.numBins = float(36)
        self.querySet = query
        self.X = float(X)
        self.Xm = float(Xm)
        self.Y = float(Y)
        self.Ym = float(Ym)
        self.zText = str(histoZ)
        self.histoZ = self.create_ref_string(int(histoZr),str(histoZ))
        self.histoX = self.create_ref_string(int(histoXr),str(histoX))
        self.histoY = self.create_ref_string(int(histoYr),str(histoY))
        self.histoZr = int(histoZr)
        self.histoXr = int(histoXr)
        self.histoYr = int(histoYr)   
        self.globalMin = self.querySet.aggregate(min=Min(self.histoZ))['min']
        self.globalMax = self.querySet.aggregate(max=Max(self.histoZ))['max']
        self.zbin = math.fabs(self.globalMax-self.globalMin)/self.numBins
        self.bins = {}
    
    def query_blocks(self):
        
        x = self.X
        x1 = self.Xm
        y = self.Y
        y1 = self.Ym
        z = self.globalMin
        z1 = self.globalMax
        
        self.zlinear = True
        if z1 > 180:
            z = z1-360
            z1 = 180-self.globalMin
            zlinear = False
        elif z1 < 0 and z > 0:
            z = z1
            z1 = self.globalMin
            zlinear = False
        
        xlinear = True
        if x1 > 180:
            x = x1-360
            x1 = 180-self.X
            xlinear = False
        elif x1 < 0 and x > 0:
            x = x1
            x1 = self.X
            xlinear = False

        ylinear = True
        if y1 > 180:
            y = y1-360
            y1 = 180-self.Y
            ylinear = False
        elif y1 < 0 and y > 0:
            y = y1
            y1 = self.Y
            ylinear = False
        
        querySet = self.querySet.filter(
            (Q(**{
                '%s__gte'%self.histoX: x,
                '%s__lt'%self.histoX: x1,
            }) if (xlinear) else (
                Q(**{'%s__gte'%self.histoX: self.X}) |
                Q(**{'%s__lt'%self.histoX: x})
            )) & (Q(**{
                '%s__gte'%self.histoY: y,
                '%s__lt'%self.histoY: y1,
            }) if (ylinear) else (
                Q(**{'%s__gte'%self.histoY: self.Y}) |
                Q(**{'%s__lt'%self.histoY: y})
            ))
        )
        
        # aggregate for counting residues
        annotations = {'count':Count('id')}
        annotated_query = querySet.annotate(**annotations)
        
        # add clauses for sorting+grouping into bins
        sortz = BinSort(self.zText, offset=z, bincount=self.zbin, max=z1)
        annotated_query.annotate(z=sortz)
        annotated_query = annotated_query.extra(select={'z':sortz.aggregate.as_sql()})
        annotated_query = annotated_query.order_by('z')
        
        # limit results to just the counts and bin indices
        values = annotations.keys() + ['z']
        annotated_query = annotated_query.values(*values)
        annotated_query.query.group_by = []

        self.maxCount = 0
        for entry in annotated_query:
            key = (entry['z'])
            bin = {
                'count' : entry['count'],
                'pixCoords'   : key
            }
            self.bins[key] = bin
            if self.maxCount < bin['count']:
                self.maxCount = bin['count']
    
    def create_ref_string(self, index, property):
        if index == 0:
            prefix = ''
        elif index < 0:
            prefix = ''.join(['prev__' for i in range(index, 0)])
        else:
            prefix = ''.join(['next__' for i in range(index)])
        resString = '%s%s' % (prefix, property)
        
        return resString
    
    def HistoPlot(self):
        
        self.query_blocks()
        
        """
        This code is still a work in progress and will be changed soon.
        """
        yhash = 10
        xLength = self.maxXPix - self.minXPix
        yLength = self.maxYPix - self.minYPix
        hashYPadding = 20
        hashXPadding = 18
        
        svg = SVG()
        
        svg.rect(self.minXPix, self.minYPix, self.maxYPix, self.maxXPix, 0, '#222222', '#222222')
        svg.rect(self.minXPix, self.minYPix, self.maxYPix, self.maxXPix, 1, '#000000')
        surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, (self.maxXPix-self.minXPix), (self.maxYPix-self.minYPix))
        ctx = cairo.Context (surface)
        ctx.set_font_size (12);
        xstep = ((self.globalMax - self.globalMin)%360 if self.zText in ANGLES else (self.globalMax - self.globalMin))/ 8
        if not xstep: xstep = 45
        ystep = self.maxCount/float(8)
        
        for i in range(10):
            xtext = ((self.globalMin + xstep*i + 180)%360 - 180) if self.zText in ANGLES and self.globalMax <= 180 else (self.globalMin + xstep*i)
            xtext = '%i' % int(xtext) if not xtext%1 else '%.1f' %  xtext
            xbearing, ybearing, twidth, theight, xadvance, yadvance = ctx.text_extents(xtext)
            xlabel_x = self.minXPix+((self.maxXPix-self.minXPix)/8)*i-xbearing-twidth/2+1
            svg.text(xlabel_x, 200, xtext,11)
            ytext = ystep*i
            ytext = '%i' % int(ytext) if not ytext%1 else '%.1f' % ytext
            xbearing, ybearing, twidth, theight, xadvance, yadvance = ctx.text_extents(ytext)
            ylabel_y = (self.maxYPix - ((self.maxYPix-self.minYPix)/8)*i)
            svg.text(-1, ylabel_y, ytext,11)
            
        for i in range(9):
            svg.line((xLength+hashYPadding)-205, (self.minYPix + ((self.maxYPix-self.minYPix)/8)*i), (xLength+hashYPadding)+9-205, (self.minYPix + ((self.maxYPix-self.minYPix)/8)*i), 1, '#000000')
        
        for i in range(10):
                svg.line((self.minXPix + ((self.maxXPix-self.minXPix)/8)*i), (yLength+hashXPadding), (self.minXPix + ((self.maxXPix-self.minXPix)/8)*i), (yLength+hashXPadding)+8, 1, '#000000')

        """
        Ends here.
        """

        self.render_bars(svg)
        return svg

    def render_bars(self, svg):

        binWidth = self.maxXPix/self.numBins
              
        for i in range(0,int(self.numBins)):
            if self.bins.has_key(i):
                svg.rect(
                            (self.minXPix+(binWidth*i))+.5,
                            self.minYPix +(self.maxYPix-(self.maxYPix*(self.bins[i].get('count')/float(self.maxCount))))+.5,
                            (self.maxYPix*(self.bins[i].get('count')/float(self.maxCount)))-1,
                            binWidth-1,
                            1,
                            '#2c6a22'
                )