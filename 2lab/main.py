"""
polygons_api.py
base(15) + all-6-filters(+2) + all-decorators(+1) + all-5-aggregates(+2) + zip-utils(+1) = 20/20
"""
import itertools, functools, math, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "output")
os.makedirs(_OUT, exist_ok=True)

_PAL = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22',
        '#34495e','#e91e63','#00bcd4','#8bc34a','#ff5722','#607d8b','#795548',
        '#ff9800','#4caf50','#673ab7','#2196f3','#009688','#f44336']
_HA  = tuple(math.radians(60*i) for i in range(6))

_cross = lambda o,a,b: (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
_dist2 = lambda p: p[0]**2+p[1]**2
_side  = lambda p1,p2: math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)
_cyc   = lambda poly: zip(poly, poly[1:]+(poly[0],))
_area  = lambda poly: abs(sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in _cyc(poly)))/2
_perim = lambda poly: sum(itertools.starmap(_side, _cyc(poly)))


def visualize(it, title="p", figsize=(11,7)):
    polys = list(it)
    fig, ax = plt.subplots(figsize=figsize)
    list(map(lambda ip: ax.add_patch(MplPolygon(list(ip[1]), closed=True,
             facecolor=_PAL[ip[0]%len(_PAL)], edgecolor='black',
             alpha=.6, linewidth=1.2)), enumerate(polys)))
    ax.set_aspect('equal'); ax.autoscale(); ax.margins(.12)
    ax.set_title(title); ax.grid(True, alpha=.3); plt.tight_layout()
    f = os.path.join(_OUT, f"{title.replace(' ','_')}.png")
    plt.savefig(f, dpi=100, bbox_inches='tight'); plt.close(fig)
    print(f"  {f}  ({len(polys)})"); return polys


gen_rectangle = lambda x=0.,y=0.,w=1.,h=.6,gap=.3: map(
    lambda i: ((x+i*(w+gap),y),(x+i*(w+gap)+w,y),
               (x+i*(w+gap)+w,y+h),(x+i*(w+gap),y+h)),
    itertools.count())

gen_triangle = lambda x=0.,y=0.,side=1.,gap=.3: map(
    lambda i: ((x+i*(side+gap),y),(x+i*(side+gap)+side,y),
               (x+i*(side+gap)+side/2, y+side*math.sqrt(3)/2)),
    itertools.count())

gen_hexagon = lambda x=0.,y=0.,r=.5,gap=.1: map(
    lambda i: tuple(map(
        lambda a: (x+i*(r*math.sqrt(3)+gap)+r*math.sin(a), y+r*math.cos(a)), _HA)),
    itertools.count())


tr_translate = lambda dx,dy: lambda poly: tuple((x+dx,y+dy) for x,y in poly)
tr_homothety = lambda k,cx=0.,cy=0.: lambda poly: tuple((cx+k*(x-cx),cy+k*(y-cy)) for x,y in poly)
tr_symmetry  = lambda ax='x',v=0.: lambda poly: (
    tuple((x,2*v-y) for x,y in poly) if ax=='x' else tuple((2*v-x,y) for x,y in poly))

def tr_rotate(deg, cx=0., cy=0.):
    c,s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return lambda poly: tuple((c*(x-cx)-s*(y-cy)+cx, s*(x-cx)+c*(y-cy)+cy) for x,y in poly)


def flt_convex_polygon(poly):
    trip = zip(poly, poly[1:]+(poly[0],), poly[2:]+(poly[:2]))
    sg = tuple(filter(lambda v: abs(v)>1e-10, map(lambda t: _cross(*t), trip)))
    return not sg or all(map(lambda v: v>0,sg)) or all(map(lambda v: v<0,sg))

flt_angle_point = lambda pt: lambda poly: any(map(
    lambda v: abs(v[0]-pt[0])<1e-9 and abs(v[1]-pt[1])<1e-9, poly))
flt_square      = lambda ma: lambda poly: _area(poly)<ma
flt_short_side  = lambda ml: lambda poly: min(itertools.starmap(_side,_cyc(poly)))<ml

def flt_point_inside(point):
    px,py = point
    def _p(poly):
        if not flt_convex_polygon(poly): return False
        sg = tuple(filter(lambda v: abs(v)>1e-10,
                   map(lambda e: _cross(e[0],e[1],(px,py)), _cyc(poly))))
        return not sg or all(map(lambda v: v>0,sg)) or all(map(lambda v: v<0,sg))
    return _p

flt_polygon_angles_inside = lambda op: lambda poly: flt_convex_polygon(poly) and \
    any(map(lambda pt: flt_point_inside(pt)(poly), op))


_is_seq  = lambda o: hasattr(o,'__iter__') and not isinstance(o,(str,tuple))
_flt_dec = lambda f: lambda fn: functools.wraps(fn)(lambda *a,**k: fn(
    *(filter(f,x) if _is_seq(x) else x for x in a),**k))
_tr_dec  = lambda t: lambda fn: functools.wraps(fn)(lambda *a,**k: fn(
    *(map(t,x) if _is_seq(x) else x for x in a),**k))

flt_convex_dec                = _flt_dec(flt_convex_polygon)
flt_square_dec                = lambda ma: _flt_dec(flt_square(ma))
flt_short_side_dec            = lambda ml: _flt_dec(flt_short_side(ml))
flt_angle_point_dec           = lambda pt: _flt_dec(flt_angle_point(pt))
flt_point_inside_dec          = lambda pt: _flt_dec(flt_point_inside(pt))
flt_polygon_angles_inside_dec = lambda p:  _flt_dec(flt_polygon_angles_inside(p))
tr_translate_dec = lambda dx,dy:        _tr_dec(tr_translate(dx,dy))
tr_rotate_dec    = lambda d,cx=0,cy=0:  _tr_dec(tr_rotate(d,cx,cy))
tr_symmetry_dec  = lambda ax='x',v=0.:  _tr_dec(tr_symmetry(ax,v))
tr_homothety_dec = lambda k,cx=0,cy=0:  _tr_dec(tr_homothety(k,cx,cy))


agr_origin_nearest = lambda it: functools.reduce(
    lambda acc,poly: (lambda v: v if acc is None or _dist2(v)<_dist2(acc) else acc)
                     (min(poly,key=_dist2)), it, None)
agr_max_side  = lambda it: functools.reduce(
    lambda acc,poly: max(acc, max(itertools.starmap(_side,_cyc(poly)))), it, 0.)
agr_min_area  = lambda it: functools.reduce(
    lambda acc,poly: _area(poly) if acc is None else min(acc,_area(poly)), it, None)
agr_perimeter = lambda it: functools.reduce(lambda acc,p: acc+_perim(p), it, 0.)
agr_area      = lambda it: functools.reduce(lambda acc,p: acc+_area(p),  it, 0.)


zip_polygons = lambda *iters: map(
    lambda g: tuple(itertools.chain.from_iterable(g)), zip(*iters))
count_2D  = lambda cols,sx=1.5,sy=1.5,x0=0.,y0=0.: map(
    lambda i: (x0+(i%cols)*sx, y0+(i//cols)*sy), itertools.count())
zip_tuple = lambda i1,i2: map(lambda ab: ab[0]+ab[1], zip(i1,i2))


if __name__ == "__main__":
    N = 7

    visualize(itertools.chain(
        itertools.islice(gen_rectangle(y=0), N),
        itertools.islice(gen_triangle(y=2), N),
        itertools.islice(gen_hexagon(y=4.3), N)
    ), "01_generators")

    base = ((0.,0.),(2.,0.),(2.,1.),(0.,1.))
    visualize(iter([base, tr_translate(3.5,0)(base), tr_rotate(45,1.,.5)(base),
                    tr_symmetry('x',-1.5)(base), tr_homothety(1.8,1.,.5)(base),
                    tr_homothety(.4,1.,.5)(base)]), "02_transforms")

    a = 30; perp = math.radians(a+90); sep=1.3
    dp = sep*math.cos(perp), sep*math.sin(perp)
    b0 = list(map(tr_rotate(a), itertools.islice(gen_rectangle(), N)))
    b1 = list(map(tr_translate(*dp), b0))
    b2 = list(map(tr_translate(2*dp[0],2*dp[1]), b0))
    visualize(itertools.chain(b0,b1,b2), "03a_three_bands")

    visualize(itertools.chain(
        map(tr_translate(0,3), itertools.islice(gen_rectangle(), N)),
        map(tr_translate(3,-1), map(tr_rotate(70), itertools.islice(gen_rectangle(), N)))
    ), "03b_intersecting")

    tt = list(itertools.islice(gen_triangle(y=.5), N))
    visualize(itertools.chain(tt, map(tr_symmetry('x'), tt)), "03c_sym_tris")

    bq = ((0.1,.1),(1.,.15),(.95,.85),(.05,.9))
    visualize(map(lambda s: tr_homothety(s)(bq),
                  [.3,.5,.7,.9,1.1,1.35,1.6,1.9,2.2]), "03d_scaled_quads")

    sample = [((0,0),(4,0),(4,2),(0,2)),((5,0),(6,0),(6,1),(5,1)),
              ((7,0),(9,0),(8,.4),(9,1),(7,1)),((0,3),(3,3),(3,6),(0,6)),
              ((4,3),(5,3),(4.5,5.)),((6,3),(8,3),(8,4),(6,4))]
    ref = ((.5,.3),(1.5,.3),(1.5,1.7),(.5,1.7))
    list(map(lambda nf: print(f"  {nf[0]}: {sum(1 for p in sample if nf[1](p))}"),
        [("convex",flt_convex_polygon),("angle_pt",flt_angle_point((0,0))),
         ("sq<5",flt_square(5.)),("short<1.5",flt_short_side(1.5)),
         ("pt_in",flt_point_inside((1,1))),("ang_in",flt_polygon_angles_inside(ref))]))

    pts = [(0.,.5,.5),(0.9,.5,.5),(1.8,1.,.6),(3.2,1.,.6),(4.6,1.,.6)]
    mk_band = lambda tx,ty: list(map(lambda xwh: tr_translate(tx,ty)(tr_rotate(30)(
        ((xwh[0],0),(xwh[0]+xwh[1],0),(xwh[0]+xwh[1],xwh[2]),(xwh[0],xwh[2])))), pts))
    all15 = mk_band(0,0)+mk_band(*dp)+mk_band(2*dp[0],2*dp[1])
    six = list(filter(flt_square(.5), all15))
    assert len(six)==6
    visualize(iter(six), "04a_six_filtered")

    q15 = list(map(lambda s: tr_homothety(s)(bq), (.15+.12*i for i in range(15))))
    sm4 = list(filter(flt_short_side(.4), q15))
    assert len(sm4)<=4
    visualize(iter(sm4), "04b_small4")

    mk_c = lambda i: ((i*2.5,0),(i*2.5+2,0),(i*2.5+2,2),(i*2.5+1,1),(i*2.5,2))
    visualize(filter(flt_convex_polygon,
        list(itertools.chain(itertools.islice(gen_rectangle(),8), map(mk_c,range(8))))),
        "04c_convex_only")

    @flt_convex_dec
    def show_c(it,t=""): return visualize(it,t)
    show_c(iter([((0,0),(3,0),(3,1),(0,1)),((4,0),(6,0),(5,.4),(6,1),(4,1)),
                 ((7,0),(9,0),(8,2))]), "05a_flt_dec")

    @tr_translate_dec(0,5)
    def shifted(it): return list(it)
    r4=list(itertools.islice(gen_rectangle(),4)); sh=shifted(iter(r4))
    print(f"  tr_dec: {r4[0][0]} -> {sh[0][0]}")
    visualize(itertools.chain(iter(r4),iter(sh)), "05b_tr_dec")

    polys=[((0,0),(4,0),(4,2),(0,2)),((5,0),(7,0),(6,2)),((8,0),(9,0),(9,1),(8,1))]
    list(map(lambda nv: print(f"  {nv[0]}={nv[1]}"),
        [("nearest",agr_origin_nearest(iter(polys))),
         ("max_side",round(agr_max_side(iter(polys)),4)),
         ("min_area",round(agr_min_area(iter(polys)),4)),
         ("perimeter",round(agr_perimeter(iter(polys)),4)),
         ("area",round(agr_area(iter(polys)),4))]))

    s1=[((1,1),(2,2),(3,1)),((11,11),(12,12),(13,11))]
    s2=[((1,-1),(2,-2),(3,-1)),((11,-11),(12,-12),(13,-11))]
    print("  zip_poly:", list(zip_polygons(iter(s1),iter(s2))))
    print("  count_2D:", list(itertools.islice(count_2D(4,1.,1.),8)))
    print("  zip_tuple:", list(zip_tuple(iter([(1,2),(3,4)]),iter([(10,20),(30,40)]))))
    visualize(itertools.chain(iter(s1),iter(s2),
                              zip_polygons(iter(s1),iter(s2))),"07a_zip_poly")
    visualize(map(lambda p: ((p[0],p[1]),(p[0]+1,p[1]),(p[0]+1,p[1]+.6),(p[0],p[1]+.6)),
                  itertools.islice(count_2D(4,1.4,1.),12)), "07b_grid")
