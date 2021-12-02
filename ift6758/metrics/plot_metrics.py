from sklearn.calibration import calibration_curve, CalibrationDisplay
from sklearn.metrics import classification_report
from sklearn.metrics import roc_curve,auc
import matplotlib.pyplot as plt # data visualization
import seaborn as sns # statistical data visualization
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix

def plot_calibration(ytrues,yscores,plot_labels=["Model-1"],n_bins=300):
    """
    :params ytrues,yscores,plot_labels: List of corresponding variable for various models/experiments
    """
    fig = plt.figure(figsize=(7.5, 7.5))
    # ax=fig.plot()
    ax = plt.axes()

    assert len(ytrues)==len(plot_labels)
    for i,(ytrue,yscore,plot_label) in enumerate(zip(ytrues,yscores,plot_labels)):
        disp = CalibrationDisplay.from_predictions(ytrue, yscore,n_bins=n_bins,name=plot_label,ax=ax,alpha=1-i/len(plot_labels))
    plt.title("Calibration Curves")
    plt.grid()
    #plt.show()

def plot_roc(ytrues,yscores,plot_labels=["model-1"]):
    """
    :params ytrues,yscores,plot_labels: List for Various Models
    """
    assert len(ytrues)==len(plot_labels)
    fprs =[]
    tprs=[]
    roc_aucs = []
    for ytrue,yscore in zip(ytrues,yscores):
        fpr,tpr,thresholds = roc_curve(ytrue, yscore)
        roc_auc = auc(fpr,tpr)
        fprs.append(fpr)
        tprs.append(tpr)
        roc_aucs.append(roc_auc)

    plt.figure()
    lw = 2
    l=[fprs,tprs,roc_aucs,plot_labels]
    for i,(fpr,tpr,roc_auc,plot_label) in  enumerate(zip(*l)):
        plt.plot(
            fpr,
            tpr,
            lw=lw,
            label=f"ROC curve (area = {roc_auc:0.3f}) for {plot_label}",
            alpha=0.7
        )
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver operating characteristic example")
    plt.legend(loc="lower right")
    #plt.show()

def plot_percentile(ytrues,yscores,bin_width=1,plot_labels=["Model1"]):
    """
    :params ytrues,yscores,plot_labels: List of corresponding variable for various models/experiments
    
    Plots Goal Rate vs Percentile && Cumulative % of goals assuming some bin width on percentiles 
    ref: pd.qcut https://pandas.pydata.org/docs/reference/api/pandas.qcut.html,
    In our use case returns which percentile the score belongs 
    TODO: Handling bin_width if it doesn't divide 100 exactly
    """
    assert len(ytrues)==len(plot_labels)

    fig, (plot1, plot2) = plt.subplots(1, 2,figsize=(15,7.5))
    
    
    num_bins = int(100/bin_width)
    for yscore,ytrue,plot_label in zip(yscores,ytrues,plot_labels):
        bin_regions=pd.qcut(yscore, q=num_bins,labels=False) # Assign 0->num_bins-1 to each cut
        goal_rate_values = np.zeros(num_bins)
        cumulative_goals_percentage=np.zeros(num_bins)
        total_goals =  np.sum(ytrue)## Since 1s are goals and 0s are shots
        for bin in range(num_bins-1,0-1,-1): ## Iterating reversely to account for cumulative goals in the same loop
            bin_bool = (bin_regions==bin) 
            bin_point_trues = ytrue[bin_bool]
            num_goals = np.sum(bin_point_trues)## Since 1s are goals and 0s are shots
            num_shots = bin_point_trues.shape[0] ## Includes goals as well
            goal_rate_values[bin]=(num_goals/num_shots)*100
            cumulative_goals_percentage[bin] = (num_goals*100.0/total_goals )
            if bin+1<=num_bins-1:
                cumulative_goals_percentage[bin]+=cumulative_goals_percentage[bin+1]


        ## Plotting
        xarray = range(0,100,bin_width)
        
        plot1.plot(
            xarray,
            goal_rate_values,
            label = plot_label,
            alpha=0.5
        )
        plot2.plot(
            xarray,
            cumulative_goals_percentage,
            label = plot_label,
            alpha=0.5
        )
    
    plot1.set_title("Goal Rate")
    plot1.set_xticks(range(0,101,10))
    plot1.set_ylabel("'%' Goals / (Shots + Goals)")
    plot1.set_xlim([100,0])
    plot1.grid()
    plot1.legend(loc="upper right")
    


    plot2.set_title("Cumulative '%' of goals")
    plot2.set_ylabel("'%' Proportion")

    plot2.set_xlim([100,0])
    plot2.grid()
    plt.setp([plot1,plot2],xlabel="Shot Probability Model Percentile")
    plot2.set_xticks(range(0,101,10))
    plot2.set_yticks(range(0,101,10))
    plot2.legend(loc="upper left")

    #plt.show()
    

def plotConfusion(Y,Ypred,title="Model1"):
    """
    :param Y: Ytrue
    :param Ypred: Predictions of a experiment

    ///TODO: Change it to multiple experiments
    """
    cm = confusion_matrix(Y,Ypred)


    cm_matrix = pd.DataFrame(data=cm, columns=['Predict:0', 'Predict:1'], 
                                    index=['Actual:0','Actual:1'])

    plt.figure(figsize=(10,5))
    sns.heatmap(cm_matrix, annot=True, fmt='d')
    plt.tight_layout()
    plt.title(title)

    print(classification_report(Y, Ypred))


