import PhotoSwipeLightbox from 'https://unpkg.com/photoswipe@5.4.3/dist/photoswipe-lightbox.esm.min.js';

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
        <div id="masonry-container" class="detail-masonry-gallery"></div>
    `;
    container.innerHTML = detailHTML;

    renderMasonry(project.detailImages);

    // Mevcut genişliği hafızaya al
    let currentWidth = window.innerWidth;
    
    window.addEventListener('resize', () => {
        // Sadece genişlik gerçekten değiştiyse (telefonu yan çevirmek gibi) yeniden çiz
        if (window.innerWidth !== currentWidth) {
            currentWidth = window.innerWidth;
            renderMasonry(project.detailImages);
        }
    });

    // 1. ADIM: PhotoSwipe'ı 'gallery' ve 'children' olmadan, serbest modda başlatıyoruz
    const lightbox = new PhotoSwipeLightbox({
        pswpModule: () => import('https://unpkg.com/photoswipe@5.4.3/dist/photoswipe.esm.min.js'),
        bgOpacity: 0.9, 
        paddingFn: (viewportSize) => {
            return { top: 30, bottom: 30, left: 30, right: 30 }; 
        }
    });
    lightbox.init();

    // 2. ADIM: Tıklama olayını biz yönetiyoruz
    const masonryContainer = document.getElementById('masonry-container');
    masonryContainer.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link) {
            e.preventDefault(); // Resmin yeni sekmede açılmasını engelle
            
            // Tıklanan resmin gerçek sırasını (index) al
            const index = parseInt(link.getAttribute('data-index'), 10);
            
            // PhotoSwipe'a orijinal sıradaki (1, 2, 3...) listeyi ve zoom yapacağı elementleri veriyoruz
            const dataSource = project.detailImages.map((imgData, i) => {
                const imgElement = masonryContainer.querySelector(`a[data-index="${i}"] img`);
                return {
                    src: imgData.src,
                    width: imgData.width,
                    height: imgData.height,
                    alt: imgData.alt,
                    element: imgElement // Açılış/kapanış animasyonunun doğru resme gitmesi için şart
                };
            });

            // Lightbox'ı bu özel sırayla ve tıklanan indeksle aç
            lightbox.loadAndOpen(index, dataSource);
        }
    });
}

function renderMasonry(images) {
    const masonryContainer = document.getElementById('masonry-container');
    if (!masonryContainer) return;

    let colCount = 1; 
    if (window.innerWidth >= 1200) colCount = 3; 
    else if (window.innerWidth >= 768) colCount = 2; 

    masonryContainer.innerHTML = '';
    let columns = [];
    
    for (let i = 0; i < colCount; i++) {
        let colDiv = document.createElement('div');
        colDiv.className = 'masonry-column';
        columns.push(colDiv);
        masonryContainer.appendChild(colDiv);
    }

    images.forEach((imgData, index) => {
        if(typeof imgData === 'string') return; 

        // 3. ADIM: Her a etiketine data-index ekliyoruz ki sırasını bilelim
        const linkHTML = `
            <a href="${imgData.src}" 
               data-index="${index}" 
               target="_blank">
                <img src="${imgData.thumb}" alt="${imgData.alt}" loading="lazy">
            </a>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = linkHTML;
        const linkElement = tempDiv.firstElementChild;
        
        const targetColumnIndex = index % colCount;
        columns[targetColumnIndex].appendChild(linkElement);
    });
}

function checkPrintMode() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('print') === 'true') {
        document.body.classList.add('print-mode');
    }
}