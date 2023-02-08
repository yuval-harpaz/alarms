function fig = rockets_heatmap(tLast,fig)

XY = readtable('~/alarms/data/alarmXY.csv');
alarm = readtable('~/alarms/data/rename.csv');
if nargin == 0
    tLast = max(alarm.time);
    fig = figure('units','normalized','position',[0.3 0 0.3 1]);
elseif isempty(tLast)
    tLast = datetime('now');
    fig = figure('units','normalized','position',[0.3 0 0.3 1]);
else
    alarm(alarm.time > tLast,:) = [];
end
col = flipud(jet(24));
for ii = 1:height(XY)
    row = ismember(alarm.loc,XY.loc{ii});
    latest = max(alarm.time(row));
    if isempty(latest)
        cc(ii,1) = nan;
    else
        cc(ii,1) = ceil(hours(tLast-latest));
    end
end
cc(cc > 24) = 24;
cc(cc == 0) = 1;
%% 
%sqrt(XY.N(ii)/pi)/2*10+3
pix2area = @(x) sqrt(x/pi)/2*10+7;
isr = importdata('~/alarms/data/isr.txt');
colorset;
% h = borders('Israel');
n = 6467;
plot(isr(1:n,1),isr(1:n,2),'Color',[0.5 0.5 0.5])
hold on;
h(2) = borders('Palestine');
h(2).Color = [0.2 0.6 0.2];
axis equal
axis off
box off
ylim([29.5 33.5])
xlim([34 35.75])
[cco,order] = sort(cc,'descend');
if height(alarm) > 0
    for jj = 1:height(XY)
        ii = order(jj);
        XY.N(ii,1) = length(unique(alarm.time(ismember(alarm.loc,XY.loc{ii}))));
        if XY.N(ii) > 0
            plot(XY.X(ii),XY.Y(ii),'.','MarkerSize',pix2area(XY.N(ii)),'Color',col(cc(ii),:));
        end
    end
end
title({['Alarms in Israel ',datestr(tLast,'dd/mm HH:MM')],' '})
set(gcf,'Color','w')

[~,txti] = ismember({'ירושלים','אשדוד','אשקלון','תל אביב','נתניה','באר שבע','דימונה','נתיבות','עכו','משגב עם','מודיעין-מכבים-רעות'},XY.loc);
city = {'Jerusalem','Ashdod','Ashkelon','Tel Aviv','Netanya','Beer Sheva','Dimona','Netivot','Acre','Q. Shemona','Modiin'};
txtx = XY.X(txti);
txty = XY.Y(txti);
txty(end) = txty(end)-0.03;
text(txtx-0.33,txty,city,'Color',[0.5 0.5 0.5])

sz = [1 10 100];
for ii = 1:3
%     hleg(ii) = plot(34.4,32+ii/10,'k.','MarkerSize',sz(ii)/3+1);
    hleg(ii) = plot(34.2,32+ii/10,'k.','MarkerSize',pix2area(sz(ii)));
end
text(34.2,32.4,'Total')
text(repmat(34.25,3,1),32+(0.1:0.1:0.3),{'1','10','100'})
% colorbar
% colormap(col)
% caxis([1 24])
%%
writetable(XY,'~/alarms/data/alarmXY.csv','Delimiter',',','WriteVariableNames',true)
if nargout == 0
    xt = cellstr(str([1:24]'));
    xt(end) = {'24+'};
    hcb = colorbar('Xtick',1.5:24/25:24,'XtickLabel',xt);
    colormap(flipud(jet(24)));
    caxis([1 24])
%     title({'Alarms in Israel',['color = hours from ',datestr(tLast,'dd/mm HH:MM')]})
    text(35.75,31,['hours from ',datestr(tLast,'dd/mm HH:MM')],'Rotation',90)
    set( hcb, 'YDir', 'reverse' );
    text(35.7,33.55,'alarm age(h)')
end
disp(XY(1:10,[1,4]))