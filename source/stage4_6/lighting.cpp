// Gate 4.6 previsualization. Original geometry and local ray casting.
#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

struct Vec {
    double x=0, y=0, z=0;
    double operator[](int i) const { return i==0?x:i==1?y:z; }
    Vec operator+(Vec r) const { return {x+r.x,y+r.y,z+r.z}; }
    Vec operator-(Vec r) const { return {x-r.x,y-r.y,z-r.z}; }
    Vec operator*(double s) const { return {x*s,y*s,z*s}; }
    Vec product(Vec r) const { return {x*r.x,y*r.y,z*r.z}; }
};
double dot(Vec a, Vec b) { return a.x*b.x+a.y*b.y+a.z*b.z; }
Vec cross(Vec a, Vec b) { return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x}; }
Vec unit(Vec a) { return a*(1/std::sqrt(dot(a,a))); }
struct Ray { Vec o,d; };
struct Material { Vec color; double grain, fiber, sheen; };
struct Hit { double t; Vec normal; int material=-1; };
struct Bounds {
    Vec low{1e9,1e9,1e9}, high{-1e9,-1e9,-1e9};
    void add(Vec p) {
        low={std::min(low.x,p.x),std::min(low.y,p.y),std::min(low.z,p.z)};
        high={std::max(high.x,p.x),std::max(high.y,p.y),std::max(high.z,p.z)};
    }
    bool intersects(Ray r, double cap) const {
        double near=0.00002,far=cap;
        for (int k=0;k<3;k++) {
            if (std::abs(r.d[k])<1e-12) {
                if (r.o[k]<low[k]-1e-8 || r.o[k]>high[k]+1e-8) return false;
                continue;
            }
            const double a=(low[k]-r.o[k]-1e-8)/r.d[k], b=(high[k]-r.o[k]+1e-8)/r.d[k];
            near=std::max(near,std::min(a,b)); far=std::min(far,std::max(a,b));
            if (far<near) return false;
        }
        return true;
    }
};
struct Triangle {
    Vec p,e1,e2,normal,center; int material;
    Triangle(Vec a,Vec b,Vec c,int m):p(a),e1(b-a),e2(c-a),normal(unit(cross(e1,e2))),
                                     center((a+b+c)*(1.0/3)),material(m) {}
    bool intersect(Ray r, Hit& h) const {
        const Vec P=cross(r.d,e2);
        const double det=dot(e1,P);
        if (std::abs(det)<1e-10) return false;
        const Vec a=r.o-p;
        const double u=dot(a,P)/det;
        if (u<0 || u>1) return false;
        const Vec Q=cross(a,e1);
        const double v=dot(r.d,Q)/det, t=dot(e2,Q)/det;
        if (v<0 || u+v>1 || t<=0.00002 || t>=h.t) return false;
        h={t,det>0?normal:normal*(-1),material};
        return true;
    }
};
struct Node { Bounds bounds; int start=0,count=0,left=-1,right=-1; };
struct Scene {
    std::vector<Material> materials;
    std::vector<Triangle> faces;
    std::vector<Node> nodes;
    int floor=0;
    int paint(int hex,double grain=0,double fiber=0,double sheen=0) {
        const auto linear=[](int byte) { return std::pow(byte/255.,2.2); };
        materials.push_back({{linear(hex>>16),linear((hex>>8)&255),linear(hex&255)},grain,fiber,sheen});
        return int(materials.size())-1;
    }
    void quad(Vec a,Vec b,Vec c,Vec d,int m) {
        faces.emplace_back(a,b,c,m); faces.emplace_back(a,c,d,m);
    }
    void panel(Vec a,Vec b,Vec c,Vec d,Vec depth,int face,int edge) {
        quad(a,b,c,d,face);
        quad(a+depth,b+depth,c+depth,d+depth,face);
        quad(a,b,b+depth,a+depth,edge); quad(b,c,c+depth,b+depth,edge);
        quad(c,d,d+depth,c+depth,edge); quad(d,a,a+depth,d+depth,edge);
    }
    void solid(Vec a,Vec b,int face,int cap,int side) {
        const Vec p{a.x,a.y,b.z}, q{b.x,a.y,b.z}, r{b.x,b.y,b.z}, s{a.x,b.y,b.z};
        const Vec A{a.x,a.y,a.z}, B{b.x,a.y,a.z}, C{b.x,b.y,a.z}, D{a.x,b.y,a.z};
        quad(p,q,r,s,cap); quad(A,B,C,D,side);
        quad(A,B,q,p,face); quad(B,C,r,q,side);
        quad(C,D,s,r,side); quad(D,A,p,s,side);
    }
    int build(int start,int end) {
        const int id=int(nodes.size()); nodes.emplace_back();
        Bounds bounds;
        for(int i=start;i<end;i++) {
            const Triangle& f=faces[i];
            bounds.add(f.p); bounds.add(f.p+f.e1); bounds.add(f.p+f.e2);
        }
        nodes[id].bounds=bounds;
        if(end-start<=5) { nodes[id].start=start; nodes[id].count=end-start; return id; }
        const Vec size=bounds.high-bounds.low;
        int axis=size.x>size.y?0:1;
        if(size.z>size[axis]) axis=2;
        const int mid=(start+end)/2;
        std::nth_element(faces.begin()+start,faces.begin()+mid,faces.begin()+end,
                         [axis](const Triangle& a,const Triangle& b){return a.center[axis]<b.center[axis];});
        const int left=build(start,mid), right=build(mid,end);
        nodes[id].left=left; nodes[id].right=right;
        return id;
    }
    bool trace(Ray r,Hit& hit,bool early=false) const {
        int stack[96]={0}, len=1;
        bool touched=false;
        while(len) {
            const Node& node=nodes[stack[--len]];
            if(!node.bounds.intersects(r,hit.t)) continue;
            if(node.count) {
                for(int j=0;j<node.count;j++) if(faces[node.start+j].intersect(r,hit)) {
                    if(early) return true;
                    touched=true;
                }
            } else {
                stack[len++]=node.left; stack[len++]=node.right;
            }
        }
        return touched;
    }
};

void carton(Scene& s, bool paper) {
    const int board=s.paint(paper?0xbda484:0x9b6841,.10,.14,.035);
    const int lining=s.paint(paper?0xdac5a6:0xb88656,.08,.09,.024);
    const int edges=s.paint(paper?0xaa8f73:0x855631,.15,.20,.02);
    const int lip=s.paint(paper?0xe3d2b7:0xbaa081,.06,.07,.02);
    const int score=s.paint(paper?0xbca588:0x99784f,.09,.08,.02);
    const double l=-2.53,r=1.56,f=-1.13,b=1.33,h=1.05;
    s.solid({l,f,.03},{r,b,.27},board,lining,board);
    s.solid({l,b-.07,.27},{r,b,h},board,lining,lining);
    s.solid({l,f,.27},{l+.075,b,h},board,lining,lining);
    s.solid({r-.07,f,.27},{r,b,h},board,lining,lining);
    s.solid({l,f,.27},{.10,f+.065,h},board,lining,lining);
    s.solid({1.24,f,.27},{r,f+.065,h},board,lining,lining);
    s.panel({l+.05,b,h},{r-.05,b,h},{r-.18,b+.91,h+.27},{l+.16,b+.91,h+.27},
            {0,0,-.044},lining,edges);
    s.panel({l,f+.05,h},{l,b-.05,h},{l-.80,b-.09,h+.015},{l-.80,f+.25,h+.24},
            {0,0,-.041},board,edges);
    s.panel({r,f+.04,h},{r,b-.04,h},{r+.71,b-.18,h+.23},{r+.80,f+.22,h-.14},
            {0,0,-.043},lining,edges);
    s.panel({l+.04,f,h},{.10,f,h},{-.02,f-.55,h-.25},{l+.17,f-.60,h-.25},
            {0,0,-.043},board,edges);
    // A single folded strip passes through the cut and seats on a thin receiving foot.
    s.panel({.16,.76,.283},{1.09,.76,.283},{1.18,f-.01,.282},{.12,f-.01,.282},
            {0,0,-.025},lip,edges);
    s.panel({.12,f-.01,.282},{1.18,f-.01,.282},{1.28,-1.49,.114},{.11,-1.49,.114},
            {0,0,-.036},lip,edges);
    s.solid({.11,-2.47,.008},{1.34,-1.49,.114},edges,lip,edges);
    s.quad({.125,-1.49,.115},{1.268,-1.49,.115},{1.27,-1.514,.115},{.125,-1.514,.115},score);
    const int parcel=s.paint(paper?0xb8a393:0x9b6748,.07,.06,.04);
    const int top=s.paint(paper?0xdcc7a9:0xc89863,.09,.13,.035);
    const int seal=s.paint(paper?0x785344:0x526866,.08,.025,.09);
    const Vec a{.34,-2.28,.114}, c{1.16,-1.76,.557};
    s.solid(a,c,parcel,top,parcel);
    s.quad({.66,-2.281,.417},{.83,-2.281,.417},{.83,-2.281,.558},{.66,-2.281,.558},seal);
    s.quad({.66,-2.28,.558},{.83,-2.28,.558},{.83,-1.76,.558},{.66,-1.76,.558},seal);
}

void southSlots(Scene& s,double x,double y,double z,int cols,int levels,double width,
                double pitch,double stride,int frame,int glass) {
    for(int level=0;level<levels;level++) for(int i=0;i<cols;i++) {
        const double a=x+i*pitch, low=z+level*stride, high=low+stride*.59;
        s.quad({a-.010,y,low-.012},{a+width+.010,y,low-.012},
               {a+width+.010,y,high+.009},{a-.010,y,high+.009},frame);
        s.quad({a,y-.002,low},{a+width,y-.002,low},{a+width,y-.002,high},{a,y-.002,high},glass);
    }
}
void eastSlots(Scene& s,double x,double y,double z,int cols,int levels,double width,
               double pitch,double stride,int glass) {
    for(int level=0;level<levels;level++) for(int i=0;i<cols;i++) {
        const double a=y+i*pitch, low=z+level*stride, high=low+stride*.59;
        s.quad({x,a,low},{x,a+width,low},{x,a+width,high},{x,a,high},glass);
    }
}

void stillCity(Scene& s) {
    const int stone=s.paint(0xaeb5a7,.105,0,.04);
    const int pale=s.paint(0xd3c7af,.10,0,.023);
    const int roof=s.paint(0x7b8988,.08,0,.07);
    const int light=s.paint(0xe4d7bf,.08,0,.055);
    const int frame=s.paint(0x8e8f81,.07,0,.045);
    const int glass=s.paint(0x4e5c55,.04,0,.15);
    const int steps=s.paint(0xa09b87,.11,0,.025);

    // Low terraced corner, with a visible front setback.
    s.solid({-2.26,-.79,.27},{-1.29,.20,.88},pale,steps,pale);
    s.solid({-2.26,-.70,.88},{-1.34,.20,1.11},pale,light,pale);
    s.solid({-2.20,-.49,1.11},{-1.42,.17,1.46},pale,light,pale);
    s.solid({-2.15,-.40,1.46},{-1.91,.01,1.54},roof,frame,roof);
    southSlots(s,-2.11,-.792,.43,4,2,.086,.195,.21,frame,glass);
    eastSlots(s,-1.288,-.63,.43,4,2,.10,.195,.21,glass);
    southSlots(s,-2.10,-.492,1.175,4,1,.091,.17,.23,frame,glass);

    // Tall, calm facade with a smaller core behind its roof setback.
    s.solid({-1.21,.13,.27},{-.20,1.08,2.18},stone,light,stone);
    s.solid({-1.25,.10,2.18},{-.16,1.12,2.25},pale,light,pale);
    s.solid({-1.12,.24,2.25},{-.30,.99,2.75},stone,light,stone);
    s.solid({-1.01,.42,2.75},{-.56,.84,2.83},pale,light,pale);
    southSlots(s,-1.10,.128,.54,5,7,.076,.17,.22,frame,glass);
    eastSlots(s,-.198,.24,.54,4,7,.085,.195,.22,glass);
    southSlots(s,-1.04,.238,2.37,4,1,.079,.17,.26,frame,glass);
    for(int i=0;i<5;i++) {
        const double x=-1.17+i*.18;
        s.solid({x,.103,.46},{x+.021,.147,2.11},light,light,pale);
    }

    // Compact shopfront on the other side of the route.
    s.solid({.36,.77,.27},{1.32,1.18,1.30},stone,light,stone);
    s.solid({.39,.65,.62},{1.29,1.18,1.12},pale,light,pale);
    s.solid({.41,.66,1.30},{1.28,1.13,1.52},pale,light,pale);
    s.solid({.34,.55,.63},{1.31,.74,.70},roof,frame,roof);
    for(int i=0;i<4;i++) {
        const double x=.39+i*.27;
        s.solid({x,.598,.27},{x+.055,.69,.64},pale,light,pale);
    }
    southSlots(s,.46,.648,.75,4,1,.105,.197,.26,frame,glass);
}

void paperCity(Scene& s) {
    const int ivory=s.paint(0xe5d2b7,.11,.18,.008);
    const int white=s.paint(0xf0e0c7,.075,.17,.01);
    const int cut=s.paint(0xc6af8b,.14,.24,.012);
    const int mid=s.paint(0xd7c0a0,.095,.16,.008);

    // Broad laminated steps. Offsets leave short shadow reveals between paper profiles.
    for(int j=0;j<8;j++) {
        const double z=.275+j*.105, x=-2.30+j*.029, y=-.76+j*.040;
        s.solid({x,y,z},{-1.27-j*.022,.06,z+.087},mid,ivory,cut);
        s.solid({x+.10,y+.065,z+.082},{-1.36-j*.017,.16,z+.103},ivory,white,cut);
    }
    s.solid({-2.03,-.33,1.09},{-1.58,-.02,1.14},ivory,white,cut);

    // Slotted fins bend at a fold. Their front sections are cut open instead of painted.
    const std::array<double,5> heights={2.07,2.33,2.70,2.58,2.38};
    for(unsigned i=0;i<heights.size();i++) {
        const double x=-1.23+i*.193, y=.13+i*.041, top=heights[i];
        const Vec depth{.027,0,0};
        s.panel({x,y,.27},{x,y+.67,.27},{x,y+.67,top-.04},{x,y,top},depth,ivory,cut);
        s.panel({x,y,1.67},{x+.157,y-.14,1.67},{x+.157,y-.14,top-.10},{x,y,top},
                {0,.027,0},white,cut);
        s.panel({x,y,.27},{x+.157,y-.14,.27},{x+.157,y-.14,1.02},{x,y,1.02},
                {0,.027,0},ivory,cut);
        s.panel({x,y,1.02},{x+.041,y-.037,1.02},{x+.041,y-.037,1.69},{x,y,1.69},
                {0,.027,0},ivory,cut);
    }

    // One hollow folded canopy with paired sides and a shared roof ridge.
    s.panel({.30,.64,.27},{1.38,.64,.27},{1.38,.64,.37},{.30,.64,.37},
            {0,.035,0},mid,cut);
    s.panel({.33,.65,.34},{.43,.65,1.01},{.49,1.18,1.01},{.37,1.18,.34},
            {.032,0,0},ivory,cut);
    s.panel({1.32,.65,.34},{1.23,.65,.91},{1.29,1.18,.91},{1.36,1.18,.34},
            {.026,0,0},mid,cut);
    s.panel({.40,.59,.99},{.77,.63,1.46},{.85,1.23,1.46},{.45,1.20,.99},
            {0,0,-.032},white,cut);
    s.panel({.77,.63,1.46},{1.28,.60,.88},{1.31,1.23,.88},{.85,1.23,1.46},
            {0,0,-.032},ivory,cut);
}

uint32_t mix(uint32_t v) {
    v^=v>>16; v*=0x7feb352dU; v^=v>>15; v*=0x846ca68bU; return v^(v>>16);
}
double random01(uint32_t& state) { state=mix(state+0x9e3779b9U); return (state>>8)*0x1p-24; }
double grain(Vec p,double cell) {
    const uint32_t x=uint32_t(int64_t(std::floor(p.x*cell)));
    const uint32_t y=uint32_t(int64_t(std::floor(p.y*cell)));
    const uint32_t z=uint32_t(int64_t(std::floor(p.z*cell)));
    return (mix(x*197339U+y*78487U+z*43351U)>>8)*0x1p-24-.5;
}
Vec diffuse(const Scene& s,Ray ray,Hit hit,uint32_t& rng,bool paper) {
    const Vec p=ray.o+ray.d*hit.t,n=hit.normal;
    const Material& material=s.materials[hit.material];
    const Vec key=paper?Vec{-3.85,-3.55,6.45}:Vec{-3.75,-4.95,7.05};
    const double radius=paper?1.05:1.65;
    const Vec light=key+Vec{(random01(rng)-.5)*2*radius,(random01(rng)-.5)*2*radius,0};
    const Vec target=light-p, direction=unit(target);
    const double dist=std::sqrt(dot(target,target));
    Hit shade{dist-.001,{},-1};
    const bool shadow=s.trace({p+n*.0004,direction},shade,true);
    const Vec tangent=unit(cross(std::abs(n.z)<.95?Vec{0,0,1}:Vec{1,0,0},n));
    const Vec bitangent=cross(n,tangent);
    const double phi=6.283185307*random01(rng), a=random01(rng);
    const Vec ambient=unit(n*std::sqrt(1-a)+(tangent*std::cos(phi)+bitangent*std::sin(phi))*std::sqrt(a));
    Hit bounce{2.5,{},-1};
    s.trace({p+n*.0004,ambient},bounce);
    const double ao=.25+.75*std::min(1.,bounce.t/1.45);
    const double energy=std::max(0.,dot(n,direction))*std::min(1.45,43./(dist*dist));
    const double sky=paper?.37:.36;
    const double fiber=grain({p.x*.21,p.y,p.z*.8},135);
    const double texture=1+material.grain*(.36*grain(p,21)+grain(p,108))+material.fiber*.34*fiber;
    const Vec fill=paper?Vec{1.0,.96,.89}:Vec{.86,.94,1.07};
    const Vec keyColor=paper?Vec{1.03,1.0,.95}:Vec{1.14,1.05,.93};
    const Vec illumination=fill*(sky*ao)+keyColor*(shadow?0:energy*.96);
    const double reflect=shadow?0:material.sheen*std::pow(std::max(0.,dot(n,unit(direction-ray.d))),22)*energy;
    return material.color.product(illumination)*texture+keyColor*reflect;
}

struct Camera {
    Vec origin,forward,right,up;
    double scale,aspect;
    Camera(bool paper,int w,int h):origin(paper?Vec{6.10,-10.95,7.03}:Vec{6.40,-11.40,6.24}),
        forward(unit(Vec{-.30,-.02,1.54}-origin)),right(unit(cross(forward,{0,0,1}))),
        up(cross(right,forward)),scale(paper?.283:.284),aspect(double(w)/h) {}
    Ray ray(double x,double y) const {
        return {origin,unit(forward+right*((2*x-1)*aspect*scale)+up*((1-2*y)*scale))};
    }
    Vec project(Vec world) const {
        const Vec v=world-origin;
        const double z=dot(v,forward);
        return {(.5+dot(v,right)/(z*2*aspect*scale)),(.5-dot(v,up)/(z*2*scale)),z};
    }
};
void ppm(const std::string& path,int w,int h,const std::vector<unsigned char>& data) {
    std::ofstream file(path,std::ios::binary);
    file<<"P6\n"<<w<<" "<<h<<"\n255\n";
    file.write(reinterpret_cast<const char*>(data.data()),data.size());
    if(!file) throw std::runtime_error("Could not write raster output");
}

int main(int argc,char** argv) {
    if(argc!=6 || (std::string(argv[1])!="a" && std::string(argv[1])!="b")) {
        std::cerr<<"usage: lighting a|b width height samples output-stem\n"; return 2;
    }
    const bool paper=std::string(argv[1])=="b";
    const int w=std::stoi(argv[2]),h=std::stoi(argv[3]),samples=std::stoi(argv[4]);
    if(w<1||h<1||samples<1||w>3600||h>4500||samples>256) return 2;
    const std::string out=argv[5];
    Scene s;
    s.floor=s.paint(paper?0xdac7ad:0xb2bdb9,.012,0,0);
    carton(s,paper);
    if(paper) paperCity(s); else stillCity(s);
    s.build(0,int(s.faces.size()));
    const Camera camera(paper,w,h);
    std::vector<unsigned char> image(w*h*3),mask(w*h*3);
    std::atomic<int> next{0};
    auto render=[&] {
        for(int y=next++;y<h;y=next++) for(int x=0;x<w;x++) {
            uint32_t rng=mix(uint32_t(y*w+x)+8411U);
            Vec color;
            int subject=0;
            for(int sample=0;sample<samples;sample++) {
                const Ray ray=camera.ray((x+random01(rng))/w,(y+random01(rng))/h);
                Hit hit{1e6,{},-1};
                if(ray.d.z<0) hit={-ray.o.z/ray.d.z,{0,0,1},s.floor};
                if(s.trace(ray,hit)) subject++;
                if(hit.material>=0) color=color+diffuse(s,ray,hit,rng,paper);
                else color=color+s.materials[s.floor].color;
            }
            for(int k=0;k<3;k++) {
                const double intensity=std::clamp(color[k]/samples,0.,1.);
                image[(y*w+x)*3+k]=static_cast<unsigned char>(std::round(255*std::pow(intensity,1/2.2)));
                mask[(y*w+x)*3+k]=static_cast<unsigned char>(std::round(255.*(samples-subject)/samples));
            }
        }
    };
    std::vector<std::thread> threads;
    const unsigned workers=std::clamp(std::thread::hardware_concurrency(),1U,12U);
    for(unsigned i=0;i<workers;i++) threads.emplace_back(render);
    for(auto& t:threads)t.join();
    ppm(out+".ppm",w,h,image); ppm(out+"-mask.ppm",w,h,mask);
    // Project the ordinary text onto the front flap using that panel's own geometry.
    const Vec leftHinge{-2.49,-1.13,1.05}, rightHinge{.10,-1.13,1.05};
    const Vec leftLip{-2.36,-1.73,.80}, rightLip{-.02,-1.68,.80};
    const auto alongFlap=[&](double u,double v) {
        const Vec hinge=leftHinge+(rightHinge-leftHinge)*u;
        const Vec lip=leftLip+(rightLip-leftLip)*u;
        return hinge+(lip-hinge)*v;
    };
    const std::array<Vec,3> marks={alongFlap(.14,.72),alongFlap(.67,.72),alongFlap(.14,.30)};
    std::cout<<std::setprecision(12);
    for(Vec world:marks) {
        const Vec p=camera.project(world);
        std::cout<<p.x*w<<" "<<p.y*h<<"\n";
    }
}
