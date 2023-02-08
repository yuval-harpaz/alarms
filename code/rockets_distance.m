function rockets_distance(grp)
if nargin == 0
    grp = [0,15.5;15.5,40.5;40.5,inf];
end

rockets = readtable('~/alarms/data/alarm.csv');
XY = readtable('~/alarms/data/alarmXY.csv');
gaza = [34.490547,31.596096;...
        34.5249,31.5715;...
        34.559166,31.546944;...
        34.558609,31.533054;...
        34.539993,31.514721;...
        34.513329,31.498608;...
        34.478607,31.471107;...
        34.4337,31.4329;...
        34.388885,31.394722;...
        34.364166,31.360832;...
        34.373604,31.314442;...
        34.334160,31.259720;...
        34.267578,31.216541];
for iloc = 1:height(XY)
    x = XY.X(iloc);
    y = XY.Y(iloc);
    dist(iloc,1) = min(sqrt((gaza(:,1)-x).^2+(gaza(:,2)-y).^2))*110;
end
XY.dist = round(dist,1);
alarm2{1} = readtable('~/alarms/data/rename2021.csv');
alarm2{2} = readtable('~/alarms/data/rename.csv');
bin = 3:3:30;

for ip = 1:2
    alarm = alarm2{ip};
    locu = unique(alarm.loc);
    alarm.dist = nan(height(alarm),1);
    for iloc = 1:length(locu)
        rowloc = ismember(XY.loc,locu{iloc});
        if sum(rowloc) == 1
            alarm.dist(ismember(alarm.loc,locu{iloc})) = XY.dist(rowloc);
        end
    end
    tot(ip) = nansum(alarm.dist);
    for igrp = 1:length(grp)
        histt(igrp,ip) = sum(alarm.dist >= grp(igrp,1) & alarm.dist < grp(igrp,2))/sum(~isnan(alarm.dist));
    end
    histtmp = hist(alarm.dist,bin);
    histr(1:length(bin),ip) = histtmp/sum(histtmp);
    histc(1:length(bin),ip) = histtmp;
    date = dateshift(alarm.time,'start','day');
    dateu = unique(date);
    means = nan(size(dateu));
    histd = [];
    for iDate = 1:length(dateu)
        means(iDate,1) = nanmean(alarm.dist(date == dateu(iDate)));
        for igrp = 1:length(grp)
            histd(iDate,igrp) = sum(alarm.dist >= grp(igrp,1) & alarm.dist < grp(igrp,2) & date == dateu(iDate));
        end
    end
    bydateCount{ip} = histd;
    bydate{ip} = table(dateu,means);
end
%%
for ii = 1:length(grp)
    tick{ii,1} = [str(grp(ii,1)),'-',str(grp(ii,2))];
end
tick = strrep(tick,'-Inf','+');
figure;
bar(100*histt);
legend('2021','2022')
ylabel('%')
xlabel('distance from Gaza (km)')
ylim([0 100])
set(gca,'XTickLabel',tick)
grid on
title('Distance of alarms from Gaza')
set(gcf,'Color','w')
shift = 0.2;
text((1:3)-0.25,5+100*histt(:,1),[str(round(100*histt(:,1))),['%';'%';'%']])
text((1:3)+0.05,5+100*histt(:,2),[str(round(100*histt(:,2))),['%';'%';'%']])
disp(round(tot))

figure;
bar(bydate{1}.means,'FaceAlpha',0.5);
hold on
bar(bydate{2}.means,'FaceAlpha',0.5);

figure;
for ip = 1:2
    subplot(1,2,ip)
    hb = bar(bydateCount{ip},'stacked');
    xlim([0 length(bydateCount{1})+1])
    ylim([0 1200])
    grid on
    title(2020+ip)
    xlabel('day')
    ylabel('alarm count')
    set(gca,'Xtick',1:length(bydateCount{1}))
end
legend(join([tick,repmat({'km'},length(tick),1)]))

figure;
subplot(1,2,1)
pie(histc(:,1),cellstr(str(bin')))
title(2021)
subplot(1,2,2)
pie(histc(:,2),cellstr(str(bin')))
title(2022)

for ii = 1:length(hb)
    co(ii,1:3) = hb(ii).FaceColor;
end
    
figure;
subplot(1,2,1)
pie(sum(bydateCount{1}),tick)
title(2021)
subplot(1,2,2)
pie(sum(bydateCount{2}),tick)
title(2022)
colormap(co); 