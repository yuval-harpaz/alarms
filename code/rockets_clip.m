time = datetime(2021,5,9)+20/24;
time = time:1/24:datetime('now');
fig = figure('units','normalized','position',[0.3 0.1 0.3 0.8]);
for ii = 1:length(time)
    fig = rockets_heatmap(time(ii),fig);
    num = '0000';
    num(end-length(str(ii))+1:end) = str(ii);
    saveas(fig,['~/alarms/data/tmp_',num,'.png'])
    pause(0.1)
    clf
    IEprog(ii)
end
fig = rockets_heatmap(time(ii),fig);
colorbar
colormap(flipud(jet(24)))
caxis([1 24])