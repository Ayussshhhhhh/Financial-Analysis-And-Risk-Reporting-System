"""Build the editable portfolio presentation (requires python-pptx)."""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUT='presentation/final_presentation.pptx'
NAVY=RGBColor(17,35,59); TEAL=RGBColor(0,153,153); PALE=RGBColor(235,244,247); WHITE=RGBColor(255,255,255); INK=RGBColor(36,51,67); MUTED=RGBColor(93,111,128)
prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
slides=[
('One governed view of regional performance','Enterprise Business Intelligence Suite | AdventureWorksDW reference implementation',['Fragmented sales, finance, workforce and supply-chain reporting delays decisions.','Build a reproducible, region-aware reporting foundation.','Audience: executives, finance, regional leaders, HR and supply chain.'],'0:00–1:00'),
('Architecture: source to decision','Local implementation with a production Azure path',['AdventureWorksDW → SQL staging → quality checks → curated star schema.','Power Query and Power BI semantic layer consume curated data.','SQL Agent is the runnable local scheduler; ADF design reuses stored procedures.','Audit status, failure branch and refresh evidence support operations.'],'1:00–2:30'),
('A shared model with explicit grain','Facts stay separate; dimensions conform',['Internet sales: one row per order line.','Inventory: one product per snapshot date.','Date, product and territory dimensions support aligned analysis.','Single-direction dimension-to-fact filters; no direct fact joins.'],'2:30–4:00'),
('Measures executives can interpret','Definitions and source boundaries matter',['Revenue, product cost, gross profit and gross margin.','YTD, prior year, YoY, MoM and rolling 3/12-month averages.','SQL and DAX definitions use explicit date context and safe division.','Gross profit is not operating profit; channel coverage is internet sales.'],'2:30–4:00'),
('Dashboard walkthrough','Pages and interactions specified for the semantic model',['Executive overview: KPIs, trend, regional comparison, category and risks.','Sales: product/customer performance and order-line drill-through.','Finance and supply-chain pages activate only where source facts support them.','Use date, region and category filters; drill-through retains filter context.'],'4:00–6:00'),
('Regional access by identity','Dynamic RLS plus workspace isolation',['Security map resolves principal to role and assigned region group.','Regional manager identities see only their group across connected facts.','Unmapped identities return no rows; executives have approved global scope.','HR and finance separation requires separate models/workspaces, not RLS alone.'],'6:00–7:30'),
('Quality and refresh are part of the product','Reconciliation before a report refresh',['Automated checks cover margin, growth, rolling averages and edge cases.','SQL checks compare row counts, sales totals, keys and date continuity.','Audit table records run status, times and errors.','SQL Server / Power BI Service checks remain pending until run in those systems.'],'7:30–8:30'),
('What is delivered','A reproducible baseline, not invented business results',['Ordered SQL scripts, M templates, DAX library, model and dashboard specs.','Access matrix, data dictionary, deployment and ADF migration design.','Six Python checks pass in the current environment.','No quantified savings are claimed without a measured baseline.'],'8:30–9:30'),
('Challenges and next steps','Connect approved sources and capture operational evidence',['AdventureWorksDW lacks a suitable HR event fact, targets and operating expense.','Add approved HR, finance and targets; validate currency and region mapping.','Run SQL reconciliation, build PBIX in Desktop, test View as and publish securely.','Capture real screenshots, refresh history and role evidence in the tenant.'],'9:30–10:00'),
('Individual reflection','Evidence of ownership and learning',['What I owned: identify specific scripts, model pages, pipeline or documentation.','Skills learned: technical and business.','Challenge, resolution and trade-offs.','Next improvement and evidence: commits, tests, DAX, SQL or report work.'],'9:30–10:00')]

def textbox(slide,x,y,w,h,text,size,color,bold=False):
    box=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf=box.text_frame; tf.clear(); tf.word_wrap=True
    p=tf.paragraphs[0]; p.text=text; p.font.name='Aptos'; p.font.size=Pt(size); p.font.bold=bold; p.font.color.rgb=color
    return box
for idx,(title,sub,bullets,timing) in enumerate(slides,1):
    s=prs.slides.add_slide(prs.slide_layouts[6]); bg=s.background.fill; bg.solid(); bg.fore_color.rgb=WHITE
    band=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width, Inches(.17)); band.fill.solid(); band.fill.fore_color.rgb=TEAL; band.line.fill.background()
    textbox(s,.65,.43,12,.55,f'{idx:02d}   {title}',27,NAVY,True)
    textbox(s,.68,1.12,11.9,.5,sub,13,MUTED)
    if idx==2:
        labels=[('SOURCE','AdventureWorksDW'),('INGEST','SQL staging'),('CURATE','Star schema'),('MODEL','Power BI'),('USERS','Secure views')]
        for j,(h,b) in enumerate(labels):
            x=.8+j*2.48
            shape=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(2.1),Inches(2.05),Inches(1.25)); shape.fill.solid(); shape.fill.fore_color.rgb=PALE; shape.line.color.rgb=TEAL
            tf=shape.text_frame; tf.clear(); tf.vertical_anchor=MSO_ANCHOR.MIDDLE
            p=tf.paragraphs[0]; p.text=h; p.alignment=PP_ALIGN.CENTER; p.font.size=Pt(11); p.font.bold=True; p.font.color.rgb=TEAL
            p=tf.add_paragraph(); p.text=b; p.alignment=PP_ALIGN.CENTER; p.font.size=Pt(15); p.font.color.rgb=NAVY
        bullets=bullets[2:]
        start=4.0
    else: start=2.05
    for j,b in enumerate(bullets):
        y=start+j*.83
        dot=s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(.86), Inches(y+.09), Inches(.13), Inches(.13)); dot.fill.solid(); dot.fill.fore_color.rgb=TEAL; dot.line.fill.background()
        textbox(s,1.17,y,11.2,.63,b,17,INK)
    foot=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.65), Inches(7.08), Inches(12), Inches(.012)); foot.fill.solid(); foot.fill.fore_color.rgb=PALE; foot.line.fill.background()
    textbox(s,.68,7.12,9,.22,'Enterprise BI Suite  •  source: AdventureWorksDW  •  implementation status documented in repository',8,MUTED)
    textbox(s,11.5,7.1,1.1,.25,timing,9,TEAL,True)
prs.save(OUT)
print(OUT)
