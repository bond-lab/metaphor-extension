# Annotation Report: annotated

## Summary

| File | Items | Senses | Pairs | Ann | Done | Part | Ign | Open | BadS | Cmts | metaphor | metonymy | hypernym | other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a-h yapılmış | 38 | 110 | 44 | 35 | 35 | 1 | 2 | 0 | 2 | 6 | 48 | 3 | 4 | 2 |
| a-k yapılmış | 11 | 41 | 31 | 11 | 11 | 0 | 0 | 0 | 2 | 0 | 25 | 2 | 0 | 0 |
| colors yapılmış | 45 | 153 | 117 | 40 | 42 | 1 | 1 | 1 | 5 | 3 | 58 | 2 | 2 | 6 |
| en a-k yapılmış | 21 | 100 | 79 | 21 | 21 | 0 | 0 | 0 | 0 | 0 | 53 | 14 | 10 | 0 |
| en renk yapılmış | 118 | 392 | 280 | 115 | 113 | 0 | 5 | 0 | 0 | 4 | 158 | 84 | 12 | 2 |
| unimet tr yapılmış | 41 | 89 | 50 | 40 | 38 | 0 | 3 | 0 | 4 | 2 | 0 | 43 | 2 | 0 |

## Comparison with ChainNet and Metaphor Thesaurus

ILI-based matching: same unordered synset pair = match, regardless of direction.

- **CN=** agree with ChainNet (same type, same direction)
- **CN↔** same type but opposite direction
- **CN≠** type disagrees  **CN?** not in ChainNet
- **TH=** pair in Metaphor Thesaurus (all thesaurus entries are metaphor)  **TH≠** found but type differs

| File | Links | CN= | CN↔ | CN≠ | CN? | TH= | TH≠ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a-h yapılmış | 57 | 1 | 0 | 0 | 11 | 1 | 1 |
| a-k yapılmış | 27 | 0 | 0 | 0 | 7 | 0 | 0 |
| colors yapılmış | 68 | 0 | 0 | 0 | 6 | 0 | 0 |
| en a-k yapılmış | 77 | 23 | 1 | 14 | 39 | 4 | 1 |
| en renk yapılmış | 256 | 85 | 21 | 47 | 103 | 29 | 3 |
| unimet tr yapılmış | 45 | 17 | 4 | 1 | 23 | 0 | 1 |

## Confusion Matrix: Annotation vs ChainNet

Rows = our annotation, Columns = ChainNet label.
Only links where ChainNet has an opinion are included.

| Our \ ChainNet | metaphor | metonymy | Row total |
| --- | --- | --- | --- |
| metaphor | **83** | 37 | 120 |
| metonymy | 8 | **69** | 77 |
| hypernym | 3 | 14 | 17 |
| Col total | 94 | 120 | 214 |

## Disagreements with ChainNet / Thesaurus

### a-h yapılmış (kenet-animal-human)

- **kobay**: annotated `hypernym` but thesaurus says `metaphor`
  - kobay — Kobaygillerden, bilimsel araştırmalarda kullanılan bir deney hayvanı
  - → kobay — Deney konusu

### en a-k yapılmış (light-dark-en)

- **black**: annotated `metaphor` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → black — black clothing (worn as a sign of mourning)
- **black**: annotated `hypernym` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → total darkness — total absence of light
- **black**: annotated `metaphor` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → black — (board games) the darker pieces
- **blackness**: annotated `hypernym` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → total darkness — total absence of light
- **blackout**: annotated `metonymy` but ChainNet has `metaphor`
  - blackout — darkness resulting from the extinction of lights (as in a city invisible to enemy aircraft)
  - → blackout — the failure of electric power for a general region
- **cloudiness**: annotated `metaphor` but ChainNet has `metonymy`
  - cloudiness — the state of the sky when it is covered by clouds
  - → cloudiness — gloomy semidarkness caused by cloud cover
- **dark**: annotated `hypernym` but ChainNet has `metonymy`
  - dark — absence of light or illumination
  - → darkness — an unilluminated area
- **darkness**: annotated `hypernym` but ChainNet has `metonymy`
  - dark — absence of light or illumination
  - → darkness — an unilluminated area
- **lighting**: annotated `metaphor` but ChainNet has `metonymy`
  - light — having abundant light or illumination
  - → ignition — the act of setting something on fire
- **night**: annotated `hypernym` but ChainNet has `metonymy`
  - night — the time after sunset and before sunrise while it is dark outside
  - → night — the dark part of the diurnal cycle considered a time unit
- **night**: annotated `hypernym` but ChainNet has `metonymy`
  - night — the time after sunset and before sunrise while it is dark outside
  - → night — the time between sunset and midnight
- **night**: annotated `metaphor` but ChainNet has `metonymy`
  - night — the time after sunset and before sunrise while it is dark outside
  - → night — the period spent sleeping
- **night**: annotated `hypernym` but ChainNet has `metonymy`
  - night — the time after sunset and before sunrise while it is dark outside
  - → night — a shortening of nightfall
- **overcast**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - cloudiness — the state of the sky when it is covered by clouds
  - → cloudiness — gloomy semidarkness caused by cloud cover
- **shadow**: annotated `hypernym` but ChainNet has `metaphor` *(also in thesaurus as metaphor)*
  - shadow — shade within clear boundaries
  - → darkness — an unilluminated area

### en renk yapılmış (color-en)

- **amber**: annotated `metonymy` but ChainNet has `metaphor` *(also in thesaurus as metaphor)*
  - amber — a deep yellow color
  - → amber — a hard yellowish to brownish translucent fossil resin; used for jewelry
- **black**: annotated `metaphor` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → black — black clothing (worn as a sign of mourning)
- **black**: annotated `metaphor` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → black — (board games) the darker pieces
- **black**: annotated `hypernym` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → total darkness — total absence of light
- **blackness**: annotated `hypernym` but ChainNet has `metonymy`
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → total darkness — total absence of light
- **blue**: annotated `metaphor` but ChainNet has `metonymy`
  - blue — blue color or pigment; resembling the color of the clear sky in the daytime
  - → blue — blue clothing
- **blue**: annotated `metaphor` but ChainNet has `metonymy`
  - blue — blue color or pigment; resembling the color of the clear sky in the daytime
  - → amobarbital sodium — the sodium salt of amobarbital that is used as a barbiturate; used as a sedative and a hypnotic
- **blue**: annotated `metaphor` but ChainNet has `metonymy`
  - blue — blue color or pigment; resembling the color of the clear sky in the daytime
  - → blue — any organization or party whose uniforms or badges are blue
- **blue**: annotated `metaphor` but ChainNet has `metonymy`
  - blue — blue color or pigment; resembling the color of the clear sky in the daytime
  - → blue — any of numerous small butterflies of the family Lycaenidae
- **blue**: annotated `metaphor` but ChainNet has `metonymy`
  - blue — blue color or pigment; resembling the color of the clear sky in the daytime
  - → bluing — used to whiten laundry or hair or give it a bluish tinge
- **bone**: annotated `metaphor` but ChainNet has `metonymy`
  - bone — rigid connective tissue that makes up the skeleton of vertebrates
  - → bone — the porous calcified substance from which bones are made
- **buff**: annotated `metaphor` but ChainNet has `metonymy`
  - buff — a soft thick undyed leather from the skins of e.g. buffalo or oxen
  - → fan — an ardent follower and admirer
- **burgundy**: annotated `metaphor` (A→B) but ChainNet has `metaphor` in opposite direction (B→A)
  - burgundy — a dark purplish-red to blackish-red color
  - → Burgundy — red table wine from the Burgundy region of France (or any similar wine made elsewhere)
- **canary**: annotated `metonymy` but ChainNet has `metaphor`
  - canary — any of several small Old World finches
  - → canary yellow — a moderate yellow with a greenish tinge
- **caramel**: annotated `hypernym` but ChainNet has `metaphor`
  - caramel — burnt sugar; used to color and flavor food
  - → caramel — firm chewy candy made from caramelized sugar and butter and milk
- **chalk**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - chalk — a soft whitish calcite
  - → chalk — a piece of calcite or a similar substance, usually in the shape of a crayon, that is used to write or draw on blackboards or other flat surfaces
- **chalk**: annotated `metonymy` but ChainNet has `metaphor`
  - chalk — a soft whitish calcite
  - → chalk — a pure flat white with little reflectance
- **chestnut**: annotated `metaphor` but ChainNet has `metonymy`
  - chestnut — edible nut of any of various chestnut trees of the genus Castanea
  - → chestnut — the brown color of chestnuts
- **chestnut**: annotated `metaphor` but ChainNet has `metonymy`
  - chestnut — edible nut of any of various chestnut trees of the genus Castanea
  - → chestnut — any of several attractive deciduous trees yellow-brown in autumn; yield a hard wood and edible nuts in a prickly bur
- **chocolate**: annotated `metonymy` but ChainNet has `metaphor`
  - chocolate — a food made from roasted ground cacao beans
  - → cocoa — a beverage made from cocoa powder and milk and sugar; usually drunk hot
- **coffee**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - coffee — any of several small trees and shrubs native to the tropical Old World yielding coffee beans
  - → coffee bean — a seed of the coffee tree; ground to make coffee
- **coffee**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - coffee bean — a seed of the coffee tree; ground to make coffee
  - → coffee — a beverage consisting of an infusion of ground coffee beans
- **color**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - coloring material — any material used for its color
  - → color — a visual attribute of things that results from the light they emit or transmit or reflect
- **complexion**: annotated `hypernym` but ChainNet has `metonymy`
  - complexion — (obsolete) a combination of elements (of dryness and warmth or of the four humors) that was once believed to determine a person's health and temperament
  - → complexion — a combination that results from coupling or interlinking
- **copper**: annotated `metonymy` but ChainNet has `metaphor`
  - copper — a ductile malleable reddish-brown corrosion-resistant diamagnetic metallic element; occurs in various minerals but is the only metal that occurs abundantly in large masses; used as an electrical and thermal conductor
  - → copper — any of various small butterflies of the family Lycaenidae having coppery wings
- **coral**: annotated `metaphor` but ChainNet has `metonymy`
  - coral — unfertilized lobster roe; reddens in cooking; used as garnish or to color sauces
  - → coral — a variable color averaging a deep pink
- **darkness**: annotated `metaphor` but ChainNet has `metonymy`
  - dark — absence of light or illumination
  - → darkness — having a dark or somber color
- **darkness**: annotated `hypernym` but ChainNet has `metonymy`
  - dark — absence of light or illumination
  - → darkness — an unilluminated area
- **dun**: annotated `metonymy` but ChainNet has `metaphor`
  - dun — a color or pigment varying around a light grey-brown color
  - → dun — horse of a dull brownish grey color
- **ebony**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - ebony — tropical tree of southern Asia having hard dark-colored heartwood used in cabinetwork
  - → ebony — hard dark-colored heartwood of the ebony tree; used in cabinetwork and for piano keys
- **emerald**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - emerald — a green transparent form of beryl; highly valued as a gemstone
  - → emerald — a transparent piece of emerald that has been cut and polished and is valued as a precious gem
- **fairness**: annotated `hypernym` but ChainNet has `metonymy`
  - fairness — conformity with rules or standards
  - → fairness — ability to make judgments free from discrimination or dishonesty
- **fairness**: annotated `metaphor` but ChainNet has `metonymy`
  - paleness — the property of having a naturally light complexion
  - → comeliness — the quality of being good looking and attractive
- **gray**: annotated `metaphor` but ChainNet has `metonymy`
  - gray — a neutral achromatic color midway between white and black
  - → grey — any organization or party whose uniforms or badges are grey
- **green**: annotated `metaphor` but ChainNet has `metonymy`
  - green — green color or pigment; resembling the color of growing grass
  - → Green — an environmentalist who belongs to the Green Party
- **green**: annotated `metaphor` but ChainNet has `metonymy`
  - green — green color or pigment; resembling the color of growing grass
  - → greens — any of various leafy plants or their leaves and stems eaten as vegetables
- **green**: annotated `metaphor` but ChainNet has `metonymy`
  - green — green color or pigment; resembling the color of growing grass
  - → park — a piece of open land for recreational use in an urban area
- **grey**: annotated `metaphor` but ChainNet has `metonymy`
  - gray — a neutral achromatic color midway between white and black
  - → grey — any organization or party whose uniforms or badges are grey
- **grey**: annotated `metaphor` but ChainNet has `metonymy`
  - gray — a neutral achromatic color midway between white and black
  - → grey — clothing that is a grey color
- **grey**: annotated `metaphor` but ChainNet has `metonymy`
  - gray — a neutral achromatic color midway between white and black
  - → grey — horse of a light gray or whitish color
- **hazel**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - hazelnut — any of several shrubs or small trees of the genus Corylus bearing edible nuts enclosed in a leafy husk
  - → hazel — the fine-grained wood of a hazelnut tree (genus Corylus) and the hazel tree (Australian genus Pomaderris)
- **indigo**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - indigo — deciduous subshrub of southeastern Asia having pinnate leaves and clusters of red or purple flowers; a source of indigo dye
  - → anil — a blue dye obtained from plants or made synthetically
- **indigoes**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - indigo — deciduous subshrub of southeastern Asia having pinnate leaves and clusters of red or purple flowers; a source of indigo dye
  - → anil — a blue dye obtained from plants or made synthetically
- **mahogany**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - mahogany — any of various tropical timber trees of the family Meliaceae especially the genus Swietinia valued for their hard yellowish- to reddish-brown wood that is readily worked and takes a high polish
  - → mahogany — wood of any of various mahogany trees; much used for cabinetwork and furniture
- **mellowness**: annotated `metaphor` but ChainNet has `metonymy`
  - mellowness — a taste (especially of fruit) that is ripe and of full flavor
  - → fullness — the property of a sensation that is rich and pleasing
- **navy**: annotated `metaphor` but ChainNet has `metonymy`
  - navy — an organization of military vessels belonging to a country and available for sea warfare
  - → dark blue — a dark shade of blue
- **navy**: annotated `hypernym` but ChainNet has `metonymy`
  - navy — an organization of military vessels belonging to a country and available for sea warfare
  - → United States Navy — the navy of the United States of America; the agency that maintains and trains and equips combat-ready naval forces
- **olive**: annotated `metonymy` but thesaurus says `metaphor`
  - olive — small ovoid fruit of the European olive tree; important food and source of oil
  - → olive — one-seeded fruit of the European olive tree usually pickled and used as a relish
- **olive**: annotated `metaphor` but ChainNet has `metonymy` *(also in thesaurus as metaphor)*
  - olive — small ovoid fruit of the European olive tree; important food and source of oil
  - → olive — a yellow-green color of low brightness and saturation
- **pink**: annotated `metaphor` (A→B) but ChainNet has `metaphor` in opposite direction (B→A) *(also in thesaurus as metaphor)*
  - pink — any of various flowers of plants of the genus Dianthus cultivated for their fragrant flowers
  - → pink — a light shade of red
- **pink**: annotated `metaphor` but ChainNet has `metonymy`
  - pink — a light shade of red
  - → pinko — a person with mildly leftist political views
- **red**: annotated `metaphor` but ChainNet has `metonymy`
  - red — red color or pigment; the chromatic color resembling the hue of blood
  - → Bolshevik — emotionally charged terms used to refer to extreme radicals or revolutionaries
- **red**: annotated `metaphor` but ChainNet has `metonymy`
  - red — red color or pigment; the chromatic color resembling the hue of blood
  - → loss — the amount by which the cost of a business exceeds its revenue
- **rose**: annotated `metaphor` but ChainNet has `metonymy` *(also in thesaurus as metaphor)*
  - rose — any of many shrubs of the genus Rosa that bear roses
  - → rose — a dusty pink color
- **rose**: annotated `metaphor` but ChainNet has `metonymy`
  - rose — a dusty pink color
  - → blush wine — pinkish table wine from red grapes whose skins were removed after fermentation began
- **ruby**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - ruby — a transparent deep red variety of corundum; used as a gemstone and in lasers
  - → ruby — a transparent piece of ruby that has been cut and polished and is valued as a precious gem
- **sable**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - sable — marten of northern Asian forests having luxuriant dark brown fur
  - → sable — the expensive dark brown fur of the marten
- **sapphire**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - sapphire — a precious transparent stone of rich blue corundum valued as a gemstone
  - → sapphire — a transparent piece of sapphire that has been cut and polished and is valued as a precious gem
- **shade**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - shade — protective covering that protects something from direct sunlight
  - → shade — relative darkness caused by light rays being intercepted by an opaque body
- **silver**: annotated `metaphor` but ChainNet has `metonymy` *(also in thesaurus as metaphor)*
  - silver — a soft white precious univalent metallic element having the highest electrical and thermal conductivity of any metal; occurs in argentite and in free form; used in coins and jewelry and tableware and photography
  - → ash grey — a light shade of grey
- **straw**: annotated `metonymy` but ChainNet has `metaphor`
  - chaff — material consisting of seed coverings and small pieces of stem or leaves that have been separated from the seeds
  - → straw — plant fiber used e.g. for making baskets and hats or as fodder
- **tan**: annotated `metaphor` but ChainNet has `metonymy`
  - tan — a light brown the color of topaz
  - → tan — a browning of the skin resulting from exposure to the rays of the sun
- **tangerine**: annotated `hypernym` but ChainNet has `metonymy`
  - tangerine — any of various deep orange mandarins grown in the United States and southern Africa
  - → tangerine — a variety of mandarin orange
- **teal**: annotated `metaphor` (A→B) but ChainNet has `metaphor` in opposite direction (B→A)
  - teal — any of various small short-necked dabbling river ducks of Europe and America
  - → bluish green — a blue-green color or pigment
- **tone**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - note — a notation representing the pitch and duration of a musical sound
  - → tone — a steady sound without overtones
- **ultramarine**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - ultramarine — blue pigment made of powdered lapis lazuli
  - → ultramarine — a vivid blue to purple-blue color
- **undertone**: annotated `metaphor` (A→B) but ChainNet has `metaphor` in opposite direction (B→A)
  - undertone — a pale or subdued color
  - → undertone — a quiet or hushed tone of voice
- **violet**: annotated `metaphor` but ChainNet has `metonymy` *(also in thesaurus as metaphor)*
  - violet — any of numerous low-growing violas with small flowers
  - → violet — a variable color that lies beyond blue in the spectrum
- **wheat**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - wheat — annual or biennial grass having erect flower spikes and light brown grains
  - → wheat — grains of common wheat; sometimes cooked whole or cracked as cereal; usually ground into flour

### unimet tr yapılmış (unimet-Turkish)

- **devlet**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - state — the territory occupied by one of the constituent administrative districts of a nation
  - → state — the group of people comprising the government of a sovereign state
- **dut**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - mulberry — sweet usually dark purple blackberry-like fruit of any of several mulberry trees of the genus Morus
  - → mulberry tree — any of several trees of the genus Morus having edible fruit that resembles the blackberry
- **kaşmir**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - cashmere — the wool of the Kashmir goat
  - → cashmere — a soft fabric made from the wool of the Cashmere goat
- **kereviz**: annotated `hypernym` but ChainNet has `metaphor`
  - cultivated celery — widely cultivated herb with aromatic leaf stalks that are eaten raw or cooked
  - → celery — stalks eaten raw or cooked or used as seasoning
- **çilek**: annotated `metonymy` (A→B) but ChainNet has `metonymy` in opposite direction (B→A)
  - strawberry — any of various low perennial herbs with many runners and bearing white flowers followed by edible fruits having many small achenes scattered on the surface of an enlarged red pulpy berry
  - → strawberry — sweet fleshy red fruit


## Differences from UniMet Baseline

Compares our annotations against UniMet's pre-populated metonymy links.
- **type_changed**: we chose a different link type
- **removed**: UniMet had a link; we removed it
- **added**: we created a link not in UniMet

### unimet tr yapılmış (unimet-Turkish)

- **ceviz**: UniMet had `metonymy` — we removed this link
  - walnut tree — any of various trees of the genus Juglans
  - → nut — usually large hard-shelled seed
- **dert**: UniMet had `metonymy` — we removed this link
  - mournfulness — intense mournfulness
  - → grief — something that causes great unhappiness
- **devlet**: UniMet had `metonymy` — we removed this link
  - state — the group of people comprising the government of a sovereign state
  - → state — the territory occupied by one of the constituent administrative districts of a nation
- **devlet**: we added `metonymy` (not in UniMet baseline)
  - state — the territory occupied by one of the constituent administrative districts of a nation
  - → state — the group of people comprising the government of a sovereign state
- **kereviz**: UniMet `metonymy` → we annotated `hypernym`
  - cultivated celery — widely cultivated herb with aromatic leaf stalks that are eaten raw or cooked
  - → celery — stalks eaten raw or cooked or used as seasoning
- **köy**: we added `metonymy` (not in UniMet baseline)
  - hamlet — a settlement smaller than a town
  - → township — a community of people smaller than a town
- **köy**: UniMet had `metonymy` — we removed this link
  - township — a community of people smaller than a town
  - → hamlet — a settlement smaller than a town
- **lahana**: we added `metonymy` (not in UniMet baseline)
  - chou — any of various types of cabbage
  - → cabbage — any of various cultivars of the genus Brassica oleracea grown for their edible leaves or flowers
- **lahana**: UniMet had `metonymy` — we removed this link
  - cabbage — any of various cultivars of the genus Brassica oleracea grown for their edible leaves or flowers
  - → chou — any of various types of cabbage
- **muşmula**: UniMet had `metonymy` — we removed this link
  - loquat — yellow olive-sized semitropical fruit with a large free stone and relatively little flesh; used for jellies
  - → japanese plum — evergreen tree of warm regions having fuzzy yellow olive-sized fruit with a large free stone; native to China and Japan
- **muşmula**: UniMet had `metonymy` — we removed this link
  - medlar — crabapple-like fruit used for preserves
  - → japanese plum — evergreen tree of warm regions having fuzzy yellow olive-sized fruit with a large free stone; native to China and Japan
- **muşmula**: we added `metonymy` (not in UniMet baseline)
  - medlar — small deciduous Eurasian tree cultivated for its fruit that resemble crab apples
  - → medlar — crabapple-like fruit used for preserves
- **muşmula**: we added `metonymy` (not in UniMet baseline)
  - japanese plum — evergreen tree of warm regions having fuzzy yellow olive-sized fruit with a large free stone; native to China and Japan
  - → loquat — yellow olive-sized semitropical fruit with a large free stone and relatively little flesh; used for jellies
- **muşmula**: UniMet had `metonymy` — we removed this link
  - medlar — crabapple-like fruit used for preserves
  - → medlar — small deciduous Eurasian tree cultivated for its fruit that resemble crab apples
- **tavuk**: UniMet had `metonymy` — we removed this link
  - biddy — adult female chicken
  - → poulet — the flesh of a chicken used for food
- **tavuk**: we added `hypernym` (not in UniMet baseline)
  - chicken — a domestic fowl bred for flesh or eggs; believed to have been developed from the red jungle fowl
  - → biddy — adult female chicken
- **yemek**: we added `metonymy` (not in UniMet baseline)
  - eat — take in solid food
  - → food — the food served and eaten at one time
- **yemek**: UniMet had `metonymy` — we removed this link
  - food — the food served and eaten at one time
  - → eat — take in solid food
- **çilek**: we added `metonymy` (not in UniMet baseline)
  - strawberry — any of various low perennial herbs with many runners and bearing white flowers followed by edible fruits having many small achenes scattered on the surface of an enlarged red pulpy berry
  - → strawberry — sweet fleshy red fruit
- **çilek**: UniMet had `metonymy` — we removed this link
  - strawberry — sweet fleshy red fruit
  - → strawberry — any of various low perennial herbs with many runners and bearing white flowers followed by edible fruits having many small achenes scattered on the surface of an enlarged red pulpy berry
- **ülke**: we added `metonymy` (not in UniMet baseline)
  - country — the territory occupied by a nation
  - → statecraft — a politically organized body of people under a single government
- **ülke**: UniMet had `metonymy` — we removed this link
  - statecraft — a politically organized body of people under a single government
  - → country — the territory occupied by a nation


## Problematic Items

### a-h yapılmış (kenet-animal-human)

**av** — status: `done`

> not sure whether it should be metaphore

- Links annotated:
  - `metonymy` av — Bir hayvanın bir başka hayvanı yemek için yakalaması → av — Bu yollarla yakalanan hayvan
  - `metaphor` av — Bu yollarla yakalanan hayvan → av — Tuzağa düşürülen, kendisinden yararlanılan kimse
  - `hypernym` av — Bir hayvanın bir başka hayvanı yemek için yakalaması → av — Karada, denizde, gölde veya akarsularda evcil olmayan hayvanları vurma veya yakalama işi

**aygır** — status: `ignore`


**dost** — status: `done`

- Sense comment on dost — Bir şeye düşkün olan, aşırı ilgi duyan kimse: koruyan anlamı da eklenebilir
- Links annotated:
  - `metaphor` dost — Sevilen, güvenilen, yakın arkadaş, gönüldaş, iyi görüşülen kimse → dost — Sahibine sevgi gösteren hayvan
  - `metaphor` dost — Sevilen, güvenilen, yakın arkadaş, gönüldaş, iyi görüşülen kimse → metres — Evli olunduğu halde evlilik dışı ilişki kurulan, genellikle kadın, kimse
  - `metaphor` dost — Sevilen, güvenilen, yakın arkadaş, gönüldaş, iyi görüşülen kimse → dost — Bir şeye düşkün olan, aşırı ilgi duyan kimse

**ekti** — status: `done`

> ekti also has meanings like stingy, unashamed and a person who craves everything

- Links annotated:
  - `metaphor` ekti — Anası ölüp başka bir koyuna alıştırılan veya elle beslenen kuzu → ekti — Anası ve babası olmayan veya atılmış, bırakılmış çocuk

**erkek at** — status: `ignore`


**eşek** — status: `done`

> ilk ikisi aynı sözcük olabilir

- Links annotated:
  - `metaphor` eşek — Atgillerden, uzun kulaklı binek ve hizmet hayvanı → eşek — Kaba, yeteneksiz, inatçı kimse
  - `metonymy` eşek — Atgillerden, uzun kulaklı binek ve hizmet hayvanı → eşek — Duvar örme, sıva yapma vb. işlerde kullanılan dört ayaklı sehpa
  - `metaphor` eşek — Atgillerden, uzun kulaklı binek ve hizmet hayvanı → eşek — Odun kesmek için kullanılan üç veya dört ayaklı sehpa

**goril** — status: `done`

> goril o

- Links annotated:
  - `metaphor` goril — Afrika'nın Ekvator bölgesinde ormanlarda yaşayan, iri ve en güçlü bir maymun türü → goril — Koruyucu

**kobay** — status: `incomplete`

- Links annotated:
  - `hypernym` kobay — Kobaygillerden, bilimsel araştırmalarda kullanılan bir deney hayvanı → kobay — Deney konusu

**kurt** — status: `done`

- Bad sense: Kürt — Ön Asya'da yaşayan bir topluluk ve bu topluluktan olan kimse
- Links annotated:
  - `metaphor` kurt — Köpekgillerden, Avrupa, Asya ve Kuzey Amerika'da yaşayan, postu gri sarı renkli, yırtıcı, etçil memeli hayvan → kurt — Bir yeri, bir şeyi iyi bilen

**tüy sıklet** — status: `done`

> ayrıca zayıf, çelimsiz kimse anlamı da barındırıyor.

- Links annotated:
  - `metaphor` tüy sıklet — En az kilo ile yarışa sokulan at → tüy sıklet — 57 kiloda dövüşen boksör

**yeğen** — status: `done`

> yeğen kelimesi aynı zamanda yaşlı kimselerin küçükler için kullandığı seslenme sözü ve büyüklere göre tanıdık genç anlamlarını da taşır (TDK)

- Bad sense: yeğen — Tüylü dişi deve ile tek hörgüçlü erkek devenin geriye melezlenmesiyle elde edilen bir deve türü
  - ↳ böyle bir anlam TDK sözlüğünde bulunmuyor

### a-k yapılmış (light-dark-tr)

**gece** — status: `done`

- Bad sense: yaka — Bir şeyin, bir yerin bitiş kısmı veya yakını, uç, taraf
  - ↳ geçe ve gece farklı kavramlar
- Links annotated:
  - `metaphor` gece — Güneş battıktan gün ağarıncaya kadar geçen süre → gece — Bu süre içindeki karanlık
  - `metonymy` gece — Güneş battıktan gün ağarıncaya kadar geçen süre → gece — Eğlence, anma vb. amaçlarla geceleri düzenlenen toplantı

**karartı** — status: `done`

- Sense comment on karartı — Karaltı: tanım yetersiz , eklenebilecek tanım; Uzaklık ve karanlık sebebiyle kim veya ne olduğu seçilemeyen, belli belirsiz, koyu renkli biçim; karaltı (TDK)
- Links annotated:
  - `metaphor` siyahlık — Karanlık veya koyuluk → karartı — Karaltı

**peçe** — status: `done`

- Bad sense: peçe — Yıldız resimlerinin alındığı planların yüzeyinde görülen hafif karartı
  - ↳ sözlükte böyle bir tanım yok
- Links annotated:
  - `metaphor` peçe — Maske; sır; giz → peçe — Kadınların sokakta yüzlerine örttükleri ince genellikle siyah renkteki örtü
  - `metaphor` peçe — Maske; sır; giz → peçe — Bir şeyi gizlemek için üzerine çekilen örtü

### colors yapılmış (color-tr)

**ak** — status: `done`

> suçsuz olmak, temiz olmak tanımı eklenebilir

- Bad sense: ak — Bazı şeylerde beyaz bölüm
  - ↳ sözlükte böyle bir tanım yok
- Links annotated:
  - `metaphor` beyaz — Kar, süt ve benzerinin rengi → ak — Beyaz leke
  - `metaphor` beyaz — Kar, süt ve benzerinin rengi → ak — Bazı şeylerde beyaz bölüm

**al** — status: `done`

- Bad sense: hıyanet — Güveni kötüye kullanma, vefasızlık
  - ↳ günlük kullanımda aldatma anlamı yok, TDK sözlüğünde de yok
- Links annotated:
  - `metaphor` al — Kanın rengi, kızıl → allık — Kadınların süs için yanaklarına sürdükleri al boya
  - `metaphor` al — Kanın rengi, kızıl → al — Dorunun açığı, kızıla çalan at donu

**alaca** — status: `incomplete`

- Bad sense: alaca — Kötü huy
  - ↳ sözlükte böyle bir kullanım yok
- Links annotated:
  - `metonymy` alaca — Birkaç rengin karışımından oluşan renk, ala → alaca — Birkaç renkli iplikten yapılmış dokuma
  - `metaphor` alaca — Birkaç renkli iplikten yapılmış dokuma → alaca — Keklik, bıldırcın vb. kuşları avlamak için kullanılan iki renkli bez

**açıklık** — status: `open`

- Bad sense: açıklık — Gerçeği olduğu gibi yansıtma durumu
  - ↳ bu tanım zaten yazıyo 2. kez yazılmış
- Links annotated:
  - `metaphor` açıklık — Boş ve geniş yer → açıklık — Dürbün, fotoğraf makinesi vb. optik araçlarda ağız çapı, ışığın girebildiği delik

**bej** — status: `ignore`

> iki tanım da aynı şey


**don** — status: `done`

- Bad sense: kıyafet — Kuşanılacak, giyilecek şey
  - ↳ buradaki anlam külot anlamıyla eşdeğer

**sekil** — status: `done`

> şekil ve sekil farklı kavramlar, aynı başlıkta mı ele almalıyım?


### en renk yapılmış (color-en)

**colour** — status: `ignore`

> this entry has already been made. The only difference is British/American English


**colouration** — status: `ignore`

> this entry has already been made. The only difference is British/American English


**colouring** — status: `ignore`

> this entry has already been made. The only difference is British/American English


**richness** — status: `ignore`

- Links annotated:
  - `metaphor` affluence — abundant wealth → richness — a strong deep vividness of hue
  - `metaphor` affluence — abundant wealth → richness — the quality of having high intrinsic value
  - `metaphor` impressiveness — splendid or imposing in size or appearance → richness — a strong deep vividness of hue
  - `metaphor` richness — the property of producing abundantly and sustaining vigorous and luxuriant growth → profusion — the property of being extremely abundant
  - `metaphor` affluence — abundant wealth → fullness — the property of a sensation that is rich and pleasing

**tone** — status: `ignore`

> I am definitely not sure about this entry

- Links annotated:
  - `metonymy` note — a notation representing the pitch and duration of a musical sound → tone — a musical interval of two semitones
  - `metonymy` note — a notation representing the pitch and duration of a musical sound → tone — the quality of a person's voice
  - `metonymy` note — a notation representing the pitch and duration of a musical sound → tone — a steady sound without overtones
  - `metonymy` note — a notation representing the pitch and duration of a musical sound → timbre — (music) the distinctive property of a complex sound (a voice or noise or musical sound)
  - `metaphor` note — a notation representing the pitch and duration of a musical sound → spirit — the general atmosphere of a place or situation and the effect that it has on people

### unimet tr yapılmış (unimet-Turkish)

**ceviz** — status: `done`

- Bad sense: nut — usually large hard-shelled seed
  - ↳ türkçede ceviz için kullanılan tek bir kelime var, bu kelimenin bu entryde olması doğru değil
- Links annotated:
  - `metonymy` walnut — nut of any of various walnut trees having a wrinkled two-lobed seed with a hard shell → walnut tree — any of various trees of the genus Juglans

**dert** — status: `ignore`

> cygnet linklerinde de bu tanımların türkçe karşılığında dert kelimesi yok


**karpuz** — status: `ignore`

> türkçede watermelon vine karşılığı yok?

- Links annotated:
  - `metonymy` watermelon — large oblong or roundish melon with a hard green rind and sweet watery red or occasionally yellowish pulp → watermelon vine — an African melon

**keder** — status: `ignore`

- Links annotated:
  - `metonymy` mournfulness — intense mournfulness → grief — something that causes great unhappiness

**sefarethane** — status: `done`

- Bad sense: diplomatic corps — a mission serving diplomatic ends
  - ↳ türkçede böyle bir kullanım yok
- Links annotated:
  - `metonymy` embassy — a diplomatic building where ambassadors live or work → diplomatic corps — a mission serving diplomatic ends

**timsah** — status: `done`

- Bad sense: crocodile — large voracious aquatic reptile having a long snout with massive jaws and sharp teeth and a body covered with bony plates; of sluggish tropical waters
  - ↳ ili linki yanlış
- Bad sense: alligator — leather made from alligator's hide
  - ↳ crdocodile ile aynı olması gerekirdi
- Links annotated:
  - `metonymy` crocodile — large voracious aquatic reptile having a long snout with massive jaws and sharp teeth and a body covered with bony plates; of sluggish tropical waters → alligator — leather made from alligator's hide


## Agreements with ChainNet / Thesaurus

### a-h yapılmış (kenet-animal-human)

- **köstebek**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - köstebek — Köstebekgillerden, toprak altında oyduğu yuvalarda yaşayan, gözleri hemen hiç görmeyen, derisinden kürk yapılan küçük bir hayvan
  - → köstebek — Bir iş yerinden, kurumdan özellikle gizli servisten bilgi sızdıran kimse

### en a-k yapılmış (light-dark-en)

- **black**: `metaphor` agrees with Thesaurus
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → Black — a person with dark skin who comes from Africa (or whose ancestors came from Africa)
- **blackout**: `metaphor` agrees with ChainNet
  - blackout — darkness resulting from the extinction of lights (as in a city invisible to enemy aircraft)
  - → amnesia — partial or total loss of memory
- **blackout**: `metaphor` agrees with ChainNet
  - blackout — darkness resulting from the extinction of lights (as in a city invisible to enemy aircraft)
  - → blackout — a momentary loss of consciousness
- **blackout**: `metaphor` agrees with ChainNet
  - blackout — darkness resulting from the extinction of lights (as in a city invisible to enemy aircraft)
  - → blackout — a suspension of radio or tv broadcasting
- **dark**: `metaphor` agrees with ChainNet
  - dark — absence of light or illumination
  - → dark — an unenlightened state
- **dark**: `metaphor` agrees with ChainNet
  - dark — absence of light or illumination
  - → iniquity — absence of moral or spiritual values
- **darkness**: `metonymy` agrees with ChainNet
  - dark — absence of light or illumination
  - → darkness — having a dark or somber color
- **darkness**: `metaphor` agrees with ChainNet
  - dark — absence of light or illumination
  - → dark — an unenlightened state
- **darkness**: `metaphor` agrees with ChainNet
  - dark — absence of light or illumination
  - → iniquity — absence of moral or spiritual values
- **gloom**: `metaphor` agrees with Thesaurus
  - gloom — a state of partial or total darkness
  - → gloom — a feeling of melancholy apprehension
- **illumination**: `metonymy` agrees with ChainNet
  - illumination — the degree of visibility of your environment
  - → illuminance — the luminous flux incident on a unit area
- **illumination**: `metaphor` agrees with ChainNet
  - illumination — the degree of visibility of your environment
  - → clarification — an interpretation that removes obstacles to understanding
- **illumination**: `metaphor` agrees with ChainNet
  - illumination — the degree of visibility of your environment
  - → light — a condition of spiritual awareness; divine illumination
- **lighting**: `metonymy` agrees with ChainNet
  - light — having abundant light or illumination
  - → lighting — the craft of providing artificial light
- **night**: `metonymy` agrees with ChainNet
  - night — the time after sunset and before sunrise while it is dark outside
  - → night — darkness
- **night**: `metaphor` agrees with ChainNet
  - night — the time after sunset and before sunrise while it is dark outside
  - → night — a period of ignorance or backwardness or gloom
- **shade**: `metonymy` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → shade — protective covering that protects something from direct sunlight
- **shade**: `metaphor` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → shade — a representation of the effect of shadows in a picture or drawing (as by shading or darker pigment)
- **shade**: `metaphor` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → ghost — a mental representation of some haunting experience
- **shade**: `metaphor` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → shade — a position of relative inferiority
- **shadow**: `metaphor` agrees with ChainNet
  - shadow — shade within clear boundaries
  - → shadow — a dominating and pervasive presence
- **shadow**: `metaphor` agrees with ChainNet
  - shadow — shade within clear boundaries
  - → tail — a spy employed to follow someone and report their movements
- **shadow**: `metaphor` agrees with ChainNet
  - shadow — shade within clear boundaries
  - → shadow — an inseparable companion
- **shadow**: `metaphor` agrees with ChainNet
  - shadow — shade within clear boundaries
  - → apparition — something existing in perception only
- **shadow**: `metaphor` agrees with ChainNet
  - shadow — shade within clear boundaries
  - → trace — an indication that something has been present
- **somberness**: `metaphor` agrees with Thesaurus
  - gloom — a state of partial or total darkness
  - → gloom — a feeling of melancholy apprehension
- **sombreness**: `metaphor` agrees with Thesaurus
  - gloom — a state of partial or total darkness
  - → gloom — a feeling of melancholy apprehension

### en renk yapılmış (color-en)

- **alabaster**: `metaphor` agrees with ChainNet
  - alabaster — a compact fine-textured, usually white gypsum used for carving
  - → alabaster — a very light white
- **apricot**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - apricot — downy yellow to rosy-colored fruit resembling a small peach
  - → yellowish pink — a shade of pink tinged with yellow
- **apricot**: `metonymy` agrees with ChainNet
  - apricot — downy yellow to rosy-colored fruit resembling a small peach
  - → apricot — Asian tree having clusters of usually white blossoms and edible fruit resembling the peach
- **aquamarine**: `metaphor` agrees with Thesaurus
  - aquamarine — a transparent variety of beryl that is blue green in color
  - → greenish blue — a shade of blue tinged with green
- **black**: `metaphor` agrees with Thesaurus
  - black — the quality or state of the achromatic color of least lightness (bearing the least resemblance to white)
  - → Black — a person with dark skin who comes from Africa (or whose ancestors came from Africa)
- **bleach**: `metonymy` agrees with ChainNet
  - bleaching agent — an agent that makes things white or colorless
  - → bleach — the act of whitening something by bleaching it (exposing it to sunlight or using a chemical bleaching agent)
- **blue**: `metonymy` agrees with ChainNet
  - blue — blue color or pigment; resembling the color of the clear sky in the daytime
  - → blue sky — the sky as viewed during daylight
- **bone**: `metaphor` agrees with ChainNet
  - bone — rigid connective tissue that makes up the skeleton of vertebrates
  - → bone — a shade of white the color of bleached bones
- **buff**: `metaphor` agrees with ChainNet
  - buff — a soft thick undyed leather from the skins of e.g. buffalo or oxen
  - → yellowish brown — a medium to dark tan color
- **buff**: `metonymy` agrees with ChainNet
  - buff — a soft thick undyed leather from the skins of e.g. buffalo or oxen
  - → buff — an implement consisting of soft material mounted on a block; used for polishing (as in manicuring)
- **buff**: `metaphor` agrees with ChainNet
  - buff — a soft thick undyed leather from the skins of e.g. buffalo or oxen
  - → buff — bare skin; naked
- **canary**: `metaphor` agrees with ChainNet
  - canary — any of several small Old World finches
  - → fink — someone acting as an informer or decoy for the police
- **canary**: `metaphor` agrees with ChainNet
  - canary — any of several small Old World finches
  - → canary — a female singer
- **caramel**: `metaphor` agrees with ChainNet
  - caramel — burnt sugar; used to color and flavor food
  - → yellowish brown — a medium to dark tan color
- **cardinal**: `metaphor` agrees with ChainNet
  - cardinal — (Roman Catholic Church) one of a group of more than 100 prominent bishops in the Sacred College who advise the Pope and elect new Popes
  - → cardinal — a variable color averaging a vivid red
- **carnation**: `metaphor` agrees with Thesaurus
  - carnation — Eurasian plant with pink to purple-red spice-scented usually double flowers; widely cultivated in many varieties and many colors
  - → carnation — a pink or reddish-pink color
- **chalk**: `metaphor` agrees with ChainNet
  - chalk — a soft whitish calcite
  - → methamphetamine — an amphetamine derivative (trade name Methedrine) used in the form of a crystalline hydrochloride; used as a stimulant to the nervous system and as an appetite suppressant
- **charcoal**: `metonymy` agrees with ChainNet
  - charcoal — a carbonaceous material obtained by heating wood or other organic matter in the absence of air
  - → charcoal — a stick of black carbon material used for drawing
- **charcoal**: `metaphor` agrees with ChainNet
  - charcoal — a carbonaceous material obtained by heating wood or other organic matter in the absence of air
  - → charcoal — a very dark grey color
- **cherry**: `metonymy` agrees with ChainNet
  - cherry — a red fruit with a single hard stone
  - → cherry — any of numerous trees and shrubs producing a small fleshy round fruit with a single hard stone; many also produce a valuable hardwood
- **cherry**: `metonymy` agrees with ChainNet
  - cherry — any of numerous trees and shrubs producing a small fleshy round fruit with a single hard stone; many also produce a valuable hardwood
  - → cherry — wood of any of various cherry trees especially the black cherry
- **cherry**: `metaphor` agrees with ChainNet
  - cherry — a red fruit with a single hard stone
  - → cerise — a red the color of ripe cherries
- **chestnut**: `metonymy` agrees with ChainNet
  - chestnut — any of several attractive deciduous trees yellow-brown in autumn; yield a hard wood and edible nuts in a prickly bur
  - → chestnut — wood of any of various chestnut trees of the genus Castanea
- **chestnut**: `metaphor` agrees with ChainNet
  - chestnut — edible nut of any of various chestnut trees of the genus Castanea
  - → chestnut — a small horny callus on the inner surface of a horse's leg
- **chocolate**: `metaphor` agrees with ChainNet
  - chocolate — a food made from roasted ground cacao beans
  - → chocolate — a medium brown to dark-brown color
- **coffee**: `metaphor` agrees with ChainNet
  - coffee — a beverage consisting of an infusion of ground coffee beans
  - → chocolate — a medium brown to dark-brown color
- **color**: `metaphor` agrees with ChainNet
  - color — the appearance of objects (or light sources) described in terms of a person's perception of their hue and lightness (or brightness) and saturation
  - → semblance — an outward or token appearance or form that is deliberately misleading
- **color**: `metaphor` agrees with ChainNet
  - color — a visual attribute of things that results from the light they emit or transmit or reflect
  - → color — the timbre of a musical sound
- **color**: `metaphor` agrees with ChainNet
  - color — a visual attribute of things that results from the light they emit or transmit or reflect
  - → color — interest and variety and intensity
- **color**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - color — a visual attribute of things that results from the light they emit or transmit or reflect
  - → color — (physics) the characteristic of quarks that determines their role in the strong interaction
- **coloration**: `metaphor` agrees with ChainNet
  - coloration — appearance with regard to color
  - → color — the timbre of a musical sound
- **coloration**: `metonymy` agrees with ChainNet
  - coloration — appearance with regard to color
  - → coloration — choice and use of colors (as by an artist)
- **copper**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - copper — a ductile malleable reddish-brown corrosion-resistant diamagnetic metallic element; occurs in various minerals but is the only metal that occurs abundantly in large masses; used as an electrical and thermal conductor
  - → copper — a reddish-brown color resembling the color of polished copper
- **copper**: `metonymy` agrees with ChainNet
  - copper — a ductile malleable reddish-brown corrosion-resistant diamagnetic metallic element; occurs in various minerals but is the only metal that occurs abundantly in large masses; used as an electrical and thermal conductor
  - → copper — a copper penny
- **coral**: `metaphor` agrees with ChainNet
  - coral — the hard stony skeleton of a Mediterranean coral that has a delicate red or pink color and is used for jewelry
  - → coral — a variable color averaging a deep pink
- **coral**: `metonymy` agrees with ChainNet
  - coral — marine colonial polyp characterized by a calcareous skeleton; masses in a variety of shapes often forming reefs
  - → coral — the hard stony skeleton of a Mediterranean coral that has a delicate red or pink color and is used for jewelry
- **darkness**: `metaphor` agrees with ChainNet
  - dark — absence of light or illumination
  - → dark — an unenlightened state
- **darkness**: `metaphor` agrees with ChainNet
  - dark — absence of light or illumination
  - → iniquity — absence of moral or spiritual values
- **darkness**: `metaphor` agrees with ChainNet
  - darkness — having a dark or somber color
  - → darkness — a swarthy complexion
- **emerald**: `metaphor` agrees with ChainNet
  - emerald — a transparent piece of emerald that has been cut and polished and is valued as a precious gem
  - → emerald — the green color of an emerald
- **fawn**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - fawn — a young deer
  - → dun — a color or pigment varying around a light grey-brown color
- **gold**: `metonymy` agrees with ChainNet
  - gold — a soft yellow malleable ductile (trivalent and univalent) metallic element; occurs mainly as nuggets in rocks and alluvial deposits; does not react with most chemicals but is attacked by chlorine and aqua regia
  - → gold — coins made of gold
- **gold**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - gold — a soft yellow malleable ductile (trivalent and univalent) metallic element; occurs mainly as nuggets in rocks and alluvial deposits; does not react with most chemicals but is attacked by chlorine and aqua regia
  - → gold — something likened to the metal in brightness or preciousness or superiority etc.
- **gold**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - gold — a soft yellow malleable ductile (trivalent and univalent) metallic element; occurs mainly as nuggets in rocks and alluvial deposits; does not react with most chemicals but is attacked by chlorine and aqua regia
  - → amber — a deep yellow color
- **gray**: `metonymy` agrees with ChainNet
  - gray — a neutral achromatic color midway between white and black
  - → grey — clothing that is a grey color
- **gray**: `metonymy` agrees with ChainNet
  - gray — a neutral achromatic color midway between white and black
  - → grey — horse of a light gray or whitish color
- **heather**: `metaphor` agrees with ChainNet
  - heather — common Old World heath represented by many varieties; low evergreen grown widely in the northern hemisphere
  - → heather mixture — interwoven yarns of mixed colors producing muted greyish shades with flecks of color
- **ivory**: `metaphor` agrees with ChainNet
  - ivory — a hard smooth ivory colored dentine that makes up most of the tusks of elephants and walruses
  - → bone — a shade of white the color of bleached bones
- **jade**: `metaphor` agrees with ChainNet
  - jade — a semiprecious gemstone that takes a high polish; is usually green but sometimes whitish; consists of jadeite or nephrite
  - → jade green — a light green color varying from bluish green to yellowish green
- **jade**: `metaphor` agrees with ChainNet
  - hack — an old or over-worked horse
  - → adulteress — a woman adulterer
- **lavender**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - lavender — any of various Old World aromatic shrubs or subshrubs with usually mauve or blue flowers; widely cultivated
  - → lavender — a pale purple color
- **lemon**: `metonymy` agrees with ChainNet
  - lemon — yellow oval fruit with juicy acidic flesh
  - → lemon — a small evergreen tree that originated in Asia but is widely cultivated for its fruit
- **lemon**: `metonymy` agrees with ChainNet *(also in thesaurus)*
  - lemon — yellow oval fruit with juicy acidic flesh
  - → lemon — a distinctive tart flavor characteristic of lemons
- **lemon**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - lemon — yellow oval fruit with juicy acidic flesh
  - → gamboge — a strong yellow color
- **lemon**: `metaphor` agrees with Thesaurus
  - lemon — yellow oval fruit with juicy acidic flesh
  - → lemon — an artifact (especially an automobile) that is defective or unsatisfactory
- **maize**: `metaphor` agrees with ChainNet
  - corn — tall annual cereal grass bearing kernels on large ears: widely cultivated in America in many varieties; the principal cereal in Mexico and Central and South America since pre-Columbian times
  - → gamboge — a strong yellow color
- **mocha**: `metonymy` agrees with ChainNet
  - mocha — a superior dark coffee made from beans from Arabia
  - → mocha — a flavoring made from coffee mixed with chocolate
- **mocha**: `metaphor` agrees with ChainNet
  - mocha — a superior dark coffee made from beans from Arabia
  - → mocha — a dark brown color
- **ocher**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - ocher — any of various earths containing silica and alumina and ferric oxide; used as a pigment
  - → ocher — a moderate yellow-orange to orange color
- **ochre**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - ocher — any of various earths containing silica and alumina and ferric oxide; used as a pigment
  - → ocher — a moderate yellow-orange to orange color
- **olive**: `metonymy` agrees with ChainNet
  - olive — small ovoid fruit of the European olive tree; important food and source of oil
  - → olive — evergreen tree cultivated in the Mediterranean region since antiquity and now elsewhere; has edible shiny black fruits
- **orange**: `metonymy` agrees with ChainNet
  - orange — round yellow to orange fruit of any of several citrus trees
  - → orange — any citrus tree bearing oranges
- **orange**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - orange — round yellow to orange fruit of any of several citrus trees
  - → orange — orange color or pigment; any of a range of colors between red and yellow
- **peach**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - peach — downy juicy fruit with sweet yellowish or whitish flesh
  - → yellowish pink — a shade of pink tinged with yellow
- **peach**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - peach — downy juicy fruit with sweet yellowish or whitish flesh
  - → smasher — a very attractive or seductive looking woman
- **pearl**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - pearl — a smooth lustrous round structure inside the shell of a clam or oyster; much valued as a jewel
  - → bone — a shade of white the color of bleached bones
- **pearl**: `metaphor` agrees with ChainNet
  - pearl — a smooth lustrous round structure inside the shell of a clam or oyster; much valued as a jewel
  - → drop — a shape that is spherical and small
- **richness**: `metaphor` agrees with ChainNet
  - affluence — abundant wealth
  - → richness — a strong deep vividness of hue
- **richness**: `metaphor` agrees with ChainNet
  - affluence — abundant wealth
  - → richness — the quality of having high intrinsic value
- **richness**: `metaphor` agrees with ChainNet
  - affluence — abundant wealth
  - → fullness — the property of a sensation that is rich and pleasing
- **ruby**: `metaphor` agrees with Thesaurus
  - ruby — a transparent deep red variety of corundum; used as a gemstone and in lasers
  - → crimson — a deep and vivid red color
- **sable**: `metaphor` agrees with ChainNet
  - sable — the expensive dark brown fur of the marten
  - → coal black — a very dark black
- **sable**: `metonymy` agrees with ChainNet
  - sable — the expensive dark brown fur of the marten
  - → sable — a scarf (or trimming) made of sable
- **saffron**: `metonymy` agrees with ChainNet
  - saffron — Old World crocus having purple or white flowers with aromatic pungent orange stigmas used in flavoring food
  - → saffron — dried pungent stigmas of the Old World saffron crocus
- **salmon**: `metonymy` agrees with ChainNet
  - salmon — any of various large food and game fishes of northern waters; usually migrate from salt to fresh water to spawn
  - → salmon — flesh of any of various marine or freshwater fish of the family Salmonidae
- **salmon**: `metaphor` agrees with ChainNet
  - salmon — flesh of any of various marine or freshwater fish of the family Salmonidae
  - → salmon — a pale pinkish orange color
- **sapphire**: `metaphor` agrees with Thesaurus
  - sapphire — a precious transparent stone of rich blue corundum valued as a gemstone
  - → azure — a light shade of blue
- **shade**: `metaphor` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → ghost — a mental representation of some haunting experience
- **shade**: `metaphor` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → shade — a representation of the effect of shadows in a picture or drawing (as by shading or darker pigment)
- **shade**: `metaphor` agrees with ChainNet
  - shade — relative darkness caused by light rays being intercepted by an opaque body
  - → shade — a position of relative inferiority
- **silver**: `metonymy` agrees with ChainNet
  - silver — a soft white precious univalent metallic element having the highest electrical and thermal conductivity of any metal; occurs in argentite and in free form; used in coins and jewelry and tableware and photography
  - → silver — coins made of silver
- **silver**: `metonymy` agrees with ChainNet
  - silver — a soft white precious univalent metallic element having the highest electrical and thermal conductivity of any metal; occurs in argentite and in free form; used in coins and jewelry and tableware and photography
  - → silver medal — a trophy made of silver (or having the appearance of silver) that is usually awarded for winning second place in a competition
- **silver**: `metonymy` agrees with ChainNet
  - silver — a soft white precious univalent metallic element having the highest electrical and thermal conductivity of any metal; occurs in argentite and in free form; used in coins and jewelry and tableware and photography
  - → flatware — silverware eating utensils
- **straw**: `metaphor` agrees with ChainNet
  - chaff — material consisting of seed coverings and small pieces of stem or leaves that have been separated from the seeds
  - → pale yellow — a variable yellow tint; dull yellow, often diluted with white
- **straw**: `metaphor` agrees with ChainNet
  - chaff — material consisting of seed coverings and small pieces of stem or leaves that have been separated from the seeds
  - → straw — a thin paper or plastic tube used to suck liquids into the mouth
- **tangerine**: `metaphor` agrees with ChainNet *(also in thesaurus)*
  - tangerine — a variety of mandarin orange
  - → tangerine — a reddish to vivid orange color
- **tincture**: `metaphor` agrees with ChainNet
  - tincture — (pharmacology) a medicine consisting of an extract in an alcohol solution
  - → trace — an indication that something has been present
- **topaz**: `metaphor` agrees with ChainNet
  - topaz — a mineral (fluosilicate of aluminum) that occurs in crystals of various colors and is used as a gemstone
  - → tan — a light brown the color of topaz
- **topaz**: `metaphor` agrees with ChainNet
  - topaz — a mineral (fluosilicate of aluminum) that occurs in crystals of various colors and is used as a gemstone
  - → topaz — a yellow quartz
- **turquoise**: `metaphor` agrees with Thesaurus
  - turquoise — a blue to grey green mineral consisting of copper aluminum phosphate
  - → greenish blue — a shade of blue tinged with green
- **undertone**: `metaphor` agrees with Thesaurus
  - undertone — a pale or subdued color
  - → undertone — a subdued emotional quality underlying an utterance; implicit meaning
- **wheat**: `metaphor` agrees with ChainNet
  - wheat — grains of common wheat; sometimes cooked whole or cracked as cereal; usually ground into flour
  - → pale yellow — a variable yellow tint; dull yellow, often diluted with white
- **white**: `metaphor` agrees with Thesaurus
  - white — the quality or state of the achromatic color of greatest lightness (bearing the least resemblance to black)
  - → White — a member of the Caucasoid race
- **wine**: `metaphor` agrees with ChainNet
  - wine — fermented juice (of grapes especially)
  - → wine — a red as dark as red wine

### unimet tr yapılmış (unimet-Turkish)

- **ananas**: `metonymy` agrees with ChainNet
  - ananas — large sweet fleshy tropical fruit with a terminal tuft of stiff leaves; widely cultivated
  - → pineapple plant — a tropical American plant bearing a large fleshy edible fruit with a terminal tuft of stiff leaves; widely cultivated in the tropics
- **ayva**: `metonymy` agrees with ChainNet
  - quince — aromatic acid-tasting pear-shaped fruit used in preserves
  - → cydonia oblonga — small Asian tree with pinkish flowers and pear-shaped fruit; widely cultivated
- **badem**: `metonymy` agrees with ChainNet
  - almond — oval-shaped edible seed of the almond tree
  - → amygdalus communis — small bushy deciduous tree native to Asia and North Africa having pretty pink blossoms and highly prized edible nuts enclosed in a hard green hull; cultivated in southern Australia and California
- **böğürtlen**: `metonymy` agrees with ChainNet
  - blackberry — large sweet black or very dark purple edible aggregate fruit of any of various bushes of the genus Rubus
  - → blackberry — bramble with sweet edible black or dark purple berries that usually do not separate from the receptacle
- **ceviz**: `metonymy` agrees with ChainNet
  - walnut — nut of any of various walnut trees having a wrinkled two-lobed seed with a hard shell
  - → walnut tree — any of various trees of the genus Juglans
- **kayısı**: `metonymy` agrees with ChainNet
  - apricot — downy yellow to rosy-colored fruit resembling a small peach
  - → apricot tree — Asian tree having clusters of usually white blossoms and edible fruit resembling the peach
- **kiraz**: `metonymy` agrees with ChainNet
  - cherry — a red fruit with a single hard stone
  - → cherry — any of numerous trees and shrubs producing a small fleshy round fruit with a single hard stone; many also produce a valuable hardwood
- **kuzu**: `metonymy` agrees with ChainNet
  - lamb — young sheep
  - → lamb — the flesh of a young domestic sheep eaten as food
- **köy**: `metonymy` agrees with ChainNet
  - hamlet — a settlement smaller than a town
  - → township — a community of people smaller than a town
- **lahana**: `metonymy` agrees with ChainNet
  - chou — any of various types of cabbage
  - → cabbage — any of various cultivars of the genus Brassica oleracea grown for their edible leaves or flowers
- **mandalina**: `metonymy` agrees with ChainNet
  - mandarin — a somewhat flat reddish-orange loose skinned citrus of China
  - → mandarin orange tree — shrub or small tree having flattened globose fruit with very sweet aromatic pulp and thin yellow-orange to flame-orange rind that is loose and easily removed; native to southeastern Asia
- **muşmula**: `metonymy` agrees with ChainNet
  - medlar — small deciduous Eurasian tree cultivated for its fruit that resemble crab apples
  - → medlar — crabapple-like fruit used for preserves
- **portakal**: `metonymy` agrees with ChainNet
  - orange — round yellow to orange fruit of any of several citrus trees
  - → orange — any citrus tree bearing oranges
- **tavuk**: `metonymy` agrees with ChainNet *(also in thesaurus)*
  - chicken — a domestic fowl bred for flesh or eggs; believed to have been developed from the red jungle fowl
  - → poulet — the flesh of a chicken used for food
- **yün**: `metonymy` agrees with ChainNet
  - wool — fiber sheared from animals (such as sheep) and twisted into yarn for weaving
  - → wool — a fabric made from the hair of sheep
- **ülke**: `metonymy` agrees with ChainNet
  - country — the territory occupied by a nation
  - → statecraft — a politically organized body of people under a single government
- **şeftali**: `metonymy` agrees with ChainNet
  - peach — downy juicy fruit with sweet yellowish or whitish flesh
  - → peach tree — cultivated in temperate regions

