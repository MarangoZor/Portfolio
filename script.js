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

    let currentWidth = window.innerWidth;
    window.addEventListener('resize', () => {
        if (window.innerWidth !== currentWidth) {
            currentWidth = window.innerWidth;
            renderMasonry(project.detailImages);
        }
    });

    const lightbox = new PhotoSwipeLightbox({
        pswpModule: () => import('https://unpkg.com/photoswipe@5.4.3/dist/photoswipe.esm.min.js'),
        bgOpacity: 0.9, 
        paddingFn: (viewportSize) => {
            return { top: 30, bottom: 30, left: 30, right: 30 }; 
        }
    });

    // PHOTOSWIPE ÜST BARA METİN EKLEME ÖZELLİĞİ (DÜZELTİLDİ)
    lightbox.on('uiRegister', function() {
        lightbox.pswp.ui.registerElement({
            name: 'custom-caption',
            order: 9,
            isButton: false,
            appendTo: 'topBar',
            html: '',
            onInit: (el, pswp) => {
                // Slayt her değiştiğinde başlığı güncelle
                pswp.on('change', () => {
                    // Doğrudan PhotoSwipe verisindeki 'alt' alanını okuyoruz
                    const captionText = pswp.currSlide.data.alt || '';
                    el.innerHTML = captionText;
                });
            }
        });
    });

    lightbox.init();

    const masonryContainer = document.getElementById('masonry-container');
    
    // TIKLAMA OLAYI
    masonryContainer.addEventListener('click', (e) => {
        const link = e.target.closest('.masonry-item'); // Artık class'ımız masonry-item
        if (link) {
            e.preventDefault(); 
            const index = parseInt(link.getAttribute('data-index'), 10);
            
            const dataSource = project.detailImages.map((imgData, i) => {
                const imgElement = masonryContainer.querySelector(`.masonry-item[data-index="${i}"] img`);
                return {
                    src: imgData.src,
                    width: imgData.width,
                    height: imgData.height,
                    alt: imgData.alt,
                    element: imgElement 
                };
            });

            lightbox.loadAndOpen(index, dataSource);
        }
    });

    // MOBİL İÇİN DOKUNMA (TOUCH) İLE HOVER EFEKTİ
    masonryContainer.addEventListener('touchstart', (e) => {
        const link = e.target.closest('.masonry-item');
        // Ekrana her dokunuşta diğer açık hover'ları temizle
        document.querySelectorAll('.masonry-item').forEach(el => el.classList.remove('touch-hover'));
        
        // Eğer resme dokunulduysa hover class'ını ona ver
        if (link) {
            link.classList.add('touch-hover');
        }
    }, {passive: true});
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

        // Eğer açıklama metni varsa "masonry-caption" kutusunu HTML'e dahil et
        const captionHTML = imgData.alt ? `<div class="masonry-caption">${imgData.alt}</div>` : '';

        // SADECE <a> ETİKETİ DEĞİL, KAPASAYICI CLASS (.masonry-item) EKLENDİ
        const linkHTML = `
            <a href="${imgData.src}" 
               data-index="${index}" 
               class="masonry-item"
               target="_blank">
                <img src="${imgData.thumb}" alt="${imgData.alt}" loading="lazy">
                ${captionHTML}
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