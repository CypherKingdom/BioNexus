#!/bin/bash

# Sample Data Ingestion Script
# Creates sample PDF content for demonstration

set -e

echo "📄 Creating sample publications for demo..."

SAMPLE_DIR="/run/media/CypherKing/Local Disk/BioNexus/data/sample_papers"

# Create sample text files that simulate PDF content
cat > "$SAMPLE_DIR/sample_paper_1.txt" << 'EOF'
Title: Effects of Microgravity on Bone Density in Long-Duration Spaceflight

Authors: Johnson, M., Smith, K., Williams, R.

Abstract: This study examines the impact of prolonged microgravity exposure on bone mineral density in astronauts during missions lasting 6+ months aboard the International Space Station. Using dual-energy X-ray absorptiometry (DXA) scans and biochemical bone markers, we assessed changes in lumbar spine and hip bone density in 24 crew members before, during, and after spaceflight.

Methods: Participants underwent comprehensive bone health assessments including DXA scans, blood sampling for bone turnover markers (CTX, P1NP), and questionnaires regarding exercise countermeasures and nutrition. Measurements were taken at baseline (L-180 days), in-flight (when possible), and post-flight (R+30, R+90 days).

Results: Significant bone loss was observed in the lumbar spine (-1.5% ± 0.8% per month) and total hip (-1.2% ± 0.6% per month) in all subjects. Biochemical markers indicated increased bone resorption and decreased formation. Exercise countermeasures partially mitigated bone loss but did not prevent it entirely.

Discussion: The microgravity environment poses significant challenges to bone health during long-duration spaceflight. Current countermeasures show promise but require optimization. These findings have important implications for future Mars missions and extended space exploration.

Keywords: microgravity, bone density, spaceflight, osteoporosis, ISS, countermeasures
EOF

cat > "$SAMPLE_DIR/sample_paper_2.txt" << 'EOF'
Title: Cardiovascular Adaptation to Partial Gravity Environments

Authors: Davis, L., Thompson, J., Martinez, A.

Abstract: Investigation of cardiovascular responses and adaptations in simulated partial gravity environments comparable to Mars (0.38g) and the Moon (0.16g). This research addresses critical knowledge gaps for future planetary exploration missions.

Introduction: Cardiovascular deconditioning is a major concern for long-duration spaceflight. While microgravity effects are well-documented, less is known about physiological responses to partial gravity environments that crew will encounter on planetary surfaces.

Methods: Twenty-four healthy subjects participated in a 30-day bed rest study with centrifuge-simulated partial gravity exposure. Cardiovascular parameters including heart rate variability (HRV), blood pressure, cardiac output, and orthostatic tolerance were measured. Subjects were divided into three groups: Mars gravity simulation (0.38g), lunar gravity simulation (0.16g), and control (1g).

Results: Mars gravity simulation showed intermediate cardiovascular deconditioning compared to complete bed rest, with 15% reduction in orthostatic tolerance and 8% decrease in cardiac output. Lunar gravity simulation showed greater deconditioning, approaching that seen in microgravity analog studies. Heart rate variability decreased in both partial gravity groups.

Conclusions: Partial gravity environments provide some cardiovascular protection compared to microgravity, with Mars gravity showing greater benefits than lunar gravity. These findings inform exercise prescription and mission planning for surface operations.

Organisms: Human subjects, male and female, ages 25-45
Endpoints: Heart rate variability, orthostatic tolerance, cardiac output, blood pressure
Instruments: ECG monitoring, ultrasound echocardiography, tilt table testing
EOF

cat > "$SAMPLE_DIR/sample_paper_3.txt" << 'EOF'
Title: Plant Growth Responses in Controlled Space Environment Systems

Authors: Brown, S., Lee, H., Garcia, M.

Abstract: Analysis of crop yield, nutritional content, and morphological adaptations in space-based agricultural systems under LED lighting conditions. This study evaluates the feasibility of sustainable food production for long-duration space missions.

Background: Sustainable food production is essential for long-duration space missions and planetary colonies. Understanding plant responses to space environments is crucial for developing effective agricultural systems.

Methods: Arabidopsis thaliana, lettuce (Lactuca sativa), and radish (Raphanus sativus) were grown in controlled environment chambers aboard the ISS using the Vegetable Production System (Veggie). Plants were subjected to different LED lighting spectra (red, blue, red+blue combinations) and monitored for 90 days.

Results: Arabidopsis showed normal germination but altered root growth patterns in microgravity. Lettuce produced edible biomass with nutritional content comparable to ground controls. Red+blue LED combinations yielded optimal growth rates across all species. Gene expression analysis revealed upregulation of stress response pathways.

Plant Physiology: Gravitropic responses were eliminated or severely reduced in all species. Cell wall composition showed modifications, with increased lignin content. Stomatal behavior was altered, affecting gas exchange and water regulation.

Space Agriculture Applications: These findings support the feasibility of fresh food production in space environments. Recommendations include specific LED spectra combinations and growth monitoring protocols for operational missions.

Organisms: Arabidopsis thaliana, Lactuca sativa, Raphanus sativus  
Endpoints: Growth rate, biomass yield, nutritional content, gene expression
Instruments: LED growth chambers, microscopy, spectrophotometry, qPCR
EOF

echo "✅ Sample publications created in $SAMPLE_DIR"
echo "📝 Created 3 sample text files (PDF simulation)"
echo "🔧 These will be processed by the ingestion pipeline during demo"