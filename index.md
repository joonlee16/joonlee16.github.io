---
layout: default
title: "Home"
---

<!-- Page Container -->
<div style="position: relative;">

  <!-- Background Video -->
  <video autoplay muted loop playsinline
         style="position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
          transform: translateX(-25%);
                object-fit: cover; z-index: 0;">
    <source src="/pics/vid.mp4" type="video/mp4">
  </video>

  <!-- Foreground Content -->
  <div style="position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; padding: 60px 20px;">

    <!-- Profile Card -->
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center; 
                padding: 25px; max-width: 400px; border-radius: 14px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.12); background-color: rgba(255,255,255,0.85);
                transition: transform 0.3s; margin-top: 80px;">
      
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

    <!-- Bio Section -->
    <div style="max-width: 800px; margin-top: 40px; line-height: 1.7; font-size: 1rem; color: #333; background-color: rgba(255,255,255,0.85); padding: 20px; border-radius: 14px;">
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
</div>

<style>
  /* Hover effect for profile card */
  .profile-card:hover {
    transform: translateY(-5px);
  }

  /* Ensure responsive stacking */
  @media (max-width: 768px) {
    .profile-card, .bio-section {
      width: 90%;
    }
  }
</style>
