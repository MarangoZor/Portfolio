document.addEventListener('DOMContentLoaded', () => {
    const isProjectPage = window.location.pathname.includes('project.html');

    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            if (isProjectPage) {
                buildProjectDetail(data.projects);
            } else {
                buildProfile(data.profile);
                buildProjects(data.projects);
            }
            checkPrintMode();
        })
        .catch(error => console.error('Veri çekme hatası:', error));
});

function buildProfile(profile) {
    const profileBlock = document.getElementById('profile-block');
    if(!profileBlock) return; 
    
    const skillsHTML = profile.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('');
    
    // HTML yapısını fotoğraf ve metni yan yana dizebilecek şekilde kurduk
    profileBlock.innerHTML = `
        <div class="profile-container">
            <div class="profile-image-wrapper">
                <img src="${profile.profileImageUrl}" alt="${profile.name}" loading="lazy">
            </div>
            <div class="profile-content">
                
                <h1 class="profile-name">${profile.name}</h1>
                <h2 class="profile-role">${profile.role}</h2>
                <p style="margin-bottom: 0;" class="profile-bio">${profile.bio1}</p>
                <p class="profile-bio">${profile.bio2}</p>
                <div class="skills">${skillsHTML}</div>
            </div>
        </div>
    `;
}

function buildProjects(projects) {
    const grid = document.getElementById('projects-grid');
    if(!grid) return;

    projects.forEach(project => {
        const projectCard = document.createElement('article');
        projectCard.className = 'project-card';
        
        // YENİ SIRALAMA: Başlık -> Resimler -> Açıklama -> Yıl
        projectCard.innerHTML = `
            <h3 class="card-title">${project.title}</h3>
            
            <div class="preview-gallery">
                <div class="img-wrapper img-kapak"><img src="${project.previewImages.kapak}" alt="${project.title} Kapak" loading="lazy"></div>
                <div class="img-wrapper img-yan1"><img src="${project.previewImages.yan1}" alt="Detay 1" loading="lazy"></div>
                <div class="img-wrapper img-yan2"><img src="${project.previewImages.yan2}" alt="Detay 2" loading="lazy"></div>
            </div>
            
            <div class="card-footer">
                <p class="card-summary">${project.summary}</p>
                <span class="card-year">${project.year}</span>
            </div>
        `;
        
        projectCard.addEventListener('click', () => {
            window.location.href = `project.html?id=${project.id}`;
        });
        
        grid.appendChild(projectCard);
    });
}

function buildProjectDetail(projects) {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get('id');
    const container = document.getElementById('project-detail-content');
    const project = projects.find(p => p.id === projectId);

    if (!project) {
        container.innerHTML = "<h1>Proje bulunamadı.</h1>";
        return;
    }

    let detailHTML = `
        <div class="detail-header">
            <span class="detail-year">${project.year}</span>
            <h1 class="detail-title">${project.title}</h1>
            <p class="detail-summary">${project.summary}</p>
        </div>
        <div class="detail-masonry-gallery">
    `;

    project.detailImages.forEach(imgUrl => {
        detailHTML += `<img src="${imgUrl}" alt="${project.title} Görseli" loading="lazy">`;
    });

    detailHTML += `</div>`;
    container.innerHTML = detailHTML;
}

function checkPrintMode() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('print') === 'true') {
        document.body.classList.add('print-mode');
    }
}