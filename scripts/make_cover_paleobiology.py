"""COVER_LETTER_Paleobiology.docx"""
import sys, os
sys.path.insert(0, '.')
from docx import Document
from docx.shared import Pt

doc = Document()
doc.styles['Normal'].font.name = 'Times New Roman'
doc.styles['Normal'].font.size = Pt(12)

for t in [
 'Dear Editors,',
 'We submit "Beyond the oldest known individual: reconstructing mortality '
 'distributions from fossil age-at-death evidence" for consideration in '
 'Paleobiology.',
 'The paper addresses a palaeobiological problem the field has lived with '
 'for a century: fossil age-at-death evidence — histologically aged '
 'specimens, assembled life tables, and "oldest known individual" reports — '
 'does not directly identify a population mortality distribution. Our '
 'contribution is methodological but aimed squarely at palaeobiologists: a '
 'generative framework that separates the latent mortality hazard from the '
 'assemblage-formation mechanism (attritional versus catastrophic standing '
 'crop), from age-dependent preservation and recovery, and from '
 'age-estimation error, and that treats a reported maximum as the '
 'sample-size-conditioned order statistic it is.',
 'The principal validation is the extant-to-fossil degradation experiment: '
 '45 empirically known mammal life tables are degraded into fossil-like '
 'samples under a systematic grid of sample size, observation bias, age '
 'resolution, assemblage mechanism, and report type, producing an explicit '
 'map of which mortality summaries remain recoverable and which are '
 'unidentifiable. Fossil examples — Maiasaura, Psittacosaurus, '
 'Albertosaurus, and mammaliaform cementum series — appear strictly as '
 'proofs of concept and are reported as scenario ranges; where the data '
 'cannot support an estimate, the manuscript says so rather than '
 'manufacturing precision.',
 'We believe this fits Paleobiology because its questions and its '
 'constraints are the ones its readers face: what can sparse, filtered, '
 'and maximum-only fossil age evidence defensibly support. The manuscript '
 'deliberately does not equate an observed maximum with a species-level '
 'maximum lifespan, and proposes standardized reporting (E[M_50], '
 'E[M_100]) to make "oldest specimen" claims comparable across samples.',
 'All raw inputs with provenance, code, seeds, and generated outputs are '
 'included as a data-and-code bundle for reproduction; every reported '
 'number is regenerated from the supplied result files. We intend to '
 'deposit the data/code package in Dryad on acceptance, per the '
 'journal’s arrangement. The manuscript is original, is not under '
 'consideration elsewhere, and has not been published previously.',
 'Yours faithfully,',
 'The authors']:
    doc.add_paragraph(t)

doc.save('../manuscript/COVER_LETTER_Paleobiology.docx')
print('cover letter saved')
