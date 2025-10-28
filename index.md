---
layout: default
title: "Home"
---

<div style="display: flex; flex-direction: column; align-items: center; margin: 30px 20px;">

  <!-- Background Video -->
  <video autoplay muted loop playsinline
         style="position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
                width: 80%; height: auto%; object-fit: cover; z-index: 0; border-radius: 14px;">
    <source src="/pics/vid.mp4" type="video/mp4">
  </video>

  <!-- Profile Card -->
  <div style="position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; text-align: center; 
              padding: 25px; max-width: 400px; border-radius: 14px; 
              box-shadow: 0 6px 20px rgba(0,0,0,0.12); background-color: rgba(255,255,255,0.85); transition: transform 0.3s;">
    
    <img src="/pics/haejoonlee.jpg" 
         alt="Haejoon Lee, PhD Candidate in Robotics" 
         style="width: 180px; height: 180px; border-radius: 50%; object-fit: cover; margin-bottom: 15px;">

    <h1 style="margin: 0; font-size: 1.9rem;"><strong>Haejoon Lee</strong></h1>
    <p style="margin: 6px 0 15px 0; font-size: 1rem; color: #555;">
      <strong>PhD Candidate</strong> in Robotics, University of Michigan
    </p>

    <div style="font-size: 0.95rem; color: #444; line-height: 1.6;">
      📧 <a href="mailto:haejoonl@umich.edu">haejoonl@umich.edu</a><br>
      🔗 <a href="https://scholar.google.com/citations?user=W0kpJYUAAAAJ&hl=en" target="_blank">Google Scholar</a> · 
         <a href="https://github.com/joonlee16/" target="_blank">GitHub</a> · 
         <a href="https://www.linkedin.com/in/haejoon-lee-450900244/" target="_blank">LinkedIn</a>
    </div>
  </div>

  <!-- About / Bio Section -->
  <div style="max-width: 800px; margin-top: 200px; line-height: 1.7; font-size: 1rem; color: #333; position: relative; z-index:1;">
    <p>
    I am a third-year Ph.D student at the
    <a href="https://dasc-lab.github.io/" target="_blank">DASC Lab</a>, part of the 
    <a href="https://robotics.umich.edu/" target="_blank">Department of Robotics</a> at the University of Michigan, Ann Arbor. 
    I am advised by <a href="https://websites.umich.edu/~dpanagou/" target="_blank">Professor Dimitra Panagou</a>. 
    My research centers on <strong>safe, robust, and resilient multi-agent and autonomous systems</strong>, with a focus on multi-robot coordination, control, and planning in dynamic, uncertain, and potentially adversarial environments.
    </p>

    <p>
      Previously, I worked with 
      <a href="https://sites.google.com/a/stonybrook.edu/nilanjan/" target="_blank">Professor Nilanjan Chakraborty</a> at 
      <a href="https://www.stonybrook.edu/commcms/ams/" target="_blank">Stony Brook University</a> on multi-robot task allocation under uncertainties, 
      and with <a href="https://sites.google.com/site/tancaowebsite/" target="_blank">Professor Tan H. Cao</a> on multi-agent collision avoidance 
      using Moreau's Sweeping Process. I earned my Bachelor's degree in Applied Math and Statistics from 
      <a href="https://www.stonybrook.edu/commcms/ams/" target="_blank">Stony Brook University</a>.
    </p>
  </div>

</div>

<style>
  /* Hover effect for profile card */
  .about-container div:hover {
    transform: translateY(-5px);
  }

  /* Responsive adjustments */
  @media (min-width: 768px) {
    .about-container {
      flex-direction: row;
      align-items: flex-start;
      gap: 50px;
    }
    .about-container .bio-text {
      flex: 1;
    }
    .about-container div:first-child {
      flex: 0 0 300px;
    }
  }
