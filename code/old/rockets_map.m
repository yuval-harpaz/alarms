function rockets_map

json = urlread('https://services8.arcgis.com/JcXY3lLZni6BK4El/arcgis/rest/services/CITY/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json');
json = jsondecode(json);
attr = struct2table([json.features.attributes]);
geom = struct2table([json.features.geometry]);
attr = [attr,geom];
attr.MGLSDE_LOC(ismember(attr.MGLSDE_LOC,'חצור-אשדוד')) = {'חצור'};
attr.MGLSDE_LOC(ismember(attr.MGLSDE_LOC,'תל אביב -יפו')) = {'תל אביב'};
attr(ismember(attr.MGLSDE_LOC,'חצור הגלילית'),:) = [];
rockets = readtable('~/alarms/data/alarm.csv');
rockets.locOrig = rockets.loc;
rockets.loc(contains(rockets.loc,'תל אביב')) = {'תל אביב'};
rockets.loc(contains(rockets.loc,'אשקלון')) = {'אשקלון'};
rockets.loc(contains(rockets.loc,'עד הלום')) = {'אשדוד'};
rockets.loc(contains(rockets.loc,'אשדוד')) = {'אשדוד'};
rockets.loc(contains(rockets.loc,'ראשון לציון')) = {'ראשון לציון'};
rockets.loc(contains(rockets.loc,'פלמחים')) = {'פלמחים'};
% rockets.loc(ismember(rockets.loc,'בת-ים')) = {'בת ים'};
attr.MGLSDE_LOC(ismember(attr.MGLSDE_LOC,'בת ים')) = {'בת-ים'};
attr.MGLSDE_LOC(ismember(attr.MGLSDE_LOC,'אבו גוש')) = {'אבו-גוש'};
rockets.loc(contains(rockets.loc,'ירושלים')) = {'ירושלים'};
rockets.loc(contains(rockets.loc,'באר שבע')) = {'באר שבע'};
rockets.loc(contains(rockets.loc,'מודיעין')) = {'מודיעין'};
rockets.loc(contains(rockets.loc,'הרצליה')) = {'הרצליה'};
rockets.loc(contains(rockets.loc,'רמת גן')) = {'רמת גן'};
rockets.loc(contains(rockets.loc,'רמת גן')) = {'רמת גן'};
rockets.loc(contains(rockets.loc,'שדרות')) = {'שדרות'};
rockets.loc(contains(rockets.loc,'ליאון')) = {'שריגים (לי-און)'};
rockets.loc(contains(rockets.loc,'קריית גת')) = {'קריית גת'};
rockets.loc(contains(rockets.loc,'עין כרם')) = {'בית זית'};
rockets.loc(contains(rockets.loc,'נתניה')) = {'נתניה'};
rockets.loc(contains(rockets.loc,'ראש העין')) = {'ראש העין'};
rockets.loc(contains(rockets.loc,'רהט')) = {'רהט'};
rockets.loc(contains(rockets.loc,'צריפין')) = {'ראשון לציון'};
rockets.loc(contains(rockets.loc,'הרצליה')) = {'הרצלייה'};
rockets.loc(contains(rockets.loc,'קציר')) = {'קציר-חריש'};
rockets.loc(contains(rockets.loc,'יאיר')) = {'כוכב יאיר'};
rockets.loc(contains(rockets.loc,'ערערה בנגב')) = {'ערערה-בנגב'};
rockets.loc(contains(rockets.loc,'תקומה')) = {'תקומה'};
rockets.loc(contains(rockets.loc,'שגב שלום')) = {'שגב-שלום'};
rockets.loc(contains(rockets.loc,'מבטחים')) = {'מבטחים'};
rockets.loc(contains(rockets.loc,'ניר עם')) = {'ניר עם'};
rockets.loc(contains(rockets.loc,'מעגלים')) = {'מעגלים'};
rockets.loc(contains(rockets.loc,'לקיה')) = {'לקיה'};
rockets.loc(contains(rockets.loc,'דימונה')) = {'דימונה'};
rockets.loc(contains(rockets.loc,'תל ערד')) = {'כסיפה'};
rockets.loc(contains(rockets.loc,'כוחלה')) = {'כסיפה'};
rockets.loc(contains(rockets.loc,'כסייפה')) = {'כסיפה'};
rockets.loc(contains(rockets.loc,'גבים')) = {'גבים'};
rockets.loc(contains(rockets.loc,'תימורים')) = {'תימורים'};
rockets.loc(contains(rockets.loc,'רמלה')) = {'רמלה'};
rockets.loc(contains(rockets.loc,'אום בטין')) = {'תל שבע'};
rockets.loc(contains(rockets.loc,'אבו קרינאת')) = {'דימונה'};
rockets.loc(contains(rockets.loc,'אבו-תלול')) = {'דימונה'};

rockets.loc(ismember(rockets.loc,'מודיעין')) = {'מודיעין-מכבים-רעות'};
rockets.loc(ismember(rockets.loc,'סתריה')) = {'סתרייה'};
rockets.loc(ismember(rockets.loc,'שהם')) = {'שוהם'};
rockets.loc(ismember(rockets.loc,'כרמיה')) = {'כרמייה'};
rockets.loc(ismember(rockets.loc,'שדה אברהם')) = {'שדי אברהם'};
rockets.loc(ismember(rockets.loc,'צור יצחק')) = {'כוכב יאיר'};
rockets.loc(ismember(rockets.loc,'אירוס')) = {'בית עובד'};
rockets.loc(ismember(rockets.loc,'בת הדר')) = {'בית שקמה'};
rockets.loc(ismember(rockets.loc,'מעש')) = {'קריית אונו'};
rockets.loc(ismember(rockets.loc,'אבשלום')) = {'יתד'};
rockets.loc(ismember(rockets.loc,'גן שורק')) = {'נטעים'};
rockets.loc(ismember(rockets.loc,'הודיה')) = {'הודייה'};
rockets.loc(ismember(rockets.loc,'זנוח')) = {'בית שמש'};
rockets.loc(ismember(rockets.loc,'כרמית')) = {'לקיה'};
rockets.loc(ismember(rockets.loc,'מעון צופיה')) = {'בן זכאי'};
rockets.loc(ismember(rockets.loc,'באר גנים')) = {'ניר ישראל'};
rockets.loc(ismember(rockets.loc,'באר גנים')) = {'ניר ישראל'};
rockets.loc(ismember(rockets.loc,'זמרת, שובה')) = {'זמרת'};
rockets.loc(ismember(rockets.loc,'כפר מימון ותושיה')) = {'כפר מימון'};
rockets.loc(ismember(rockets.loc,'כרם ביבנה')) = {'קבוצת יבנה'};
rockets.loc(ismember(rockets.loc,'מקווה ישראל')) = {'חולון'};
rockets.loc(ismember(rockets.loc,'מתחם בני דרום')) = {'בני דרום'};
rockets.loc = strrep(rockets.loc,'תעשיון ','');
XY = readtable('~/alarms/data/alarmXY.csv');

loc = unique(rockets.loc);
loc = strrep(loc,char([39,39]),'"');
loc(ismember(loc,XY.loc)) = [];
for ii = 1:length(loc)
    row = false(height(attr),1);
    if ismember(loc{ii},attr.MGLSDE_LOC)
%     if ismember(loc{ii},{'יבנה','תלמי ביל"ו','כפר ביל"ו','טייבה','שחר','קריית יערים','עלי','סעד','כפר חב"ד','רעים','צובה','צורן'ת})
       row = ismember(attr.MGLSDE_LOC,loc{ii});
    else
        for jj = 1:height(attr)
            if contains(attr.MGLSDE_LOC{jj},loc{ii})
                row(jj) = true;
            end
        end
    end
    if sum(row) == 1
        X(ii,1) = attr.x(row);
        Y(ii,1) = attr.y(row);
    else
        X(ii,1) = nan;
        Y(ii,1) = nan;
    end
    IEprog(ii)
end

if length(loc) > 0
    missing = loc(find(isnan(X)),:);
    missing = unique(missing);
    disp(missing)
    
    
    
    
    XYnew = table(loc,X,Y);
    XYnew.N = nan(height(XYnew),1);
    XYnew(isnan(X),:) = [];
    XY = [XY;XYnew];
end
[~,order] = sort(XY.N,'descend');
XY = XY(order,:);

%% 
figure;
h = borders('Israel');
hold on;
h(2) = borders('Palestine');
h(2).Color = [0.2 0.6 0.2];
axis equal
axis off
box off
ylim([29.5 32.5])
xlim([34 35.75])

for ii = 1:height(XY)
    XY.N(ii,1) = length(unique(rockets.time(ismember(rockets.loc,XY.loc{ii}))));
    if XY.N(ii) > 0
        plot(XY.X(ii),XY.Y(ii),'.k','MarkerSize',sqrt(XY.N(ii)/pi)/2*10);
    end
end
title('Alarms in Israel')
set(gcf,'Color','w')

[~,txti] = ismember({'ירושלים','אשדוד','אשקלון','תל אביב','נתניה','באר שבע','דימונה','נתיבות'},XY.loc);
city = {'Jerusalem','Ashdod','Ashkelon','Tel Aviv','Netanya','Beer Sheva','Dimona','Netivot'};
txtx = XY.X(txti);
txty = XY.Y(txti);
text(txtx-0.3,txty,city,'Color','k')

sz = [1 10 100];
for ii = 1:3
%     hleg(ii) = plot(34.4,32+ii/10,'k.','MarkerSize',sz(ii)/3+1);
    hleg(ii) = plot(34.2,32+ii/10,'k.','MarkerSize',sqrt(sz(ii)/pi)/2*10);
end
text(repmat(34.3,3,1),32+(0.1:0.1:0.3),{'1','10','100'})

%%

writetable(XY,'~/alarms/data/alarmXY.csv','Delimiter',',','WriteVariableNames',true)
writetable(rockets,'~/alarms/data/rename.csv','Delimiter',',','WriteVariableNames',true)
